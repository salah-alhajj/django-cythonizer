import os
import sys
import shutil
import re
import time
import threading
from setuptools import setup, find_packages, Command
from setuptools.extension import Extension
from Cython.Build import cythonize
from Cython.Distutils import build_ext
from Cython.Compiler.Errors import CompileError, PyrexError
from datetime import datetime
import logging
import traceback
import io
import contextlib
from utilities import Spinner

# قائمة الملفات والمجلدات التي يجب استثناؤها من التحويل إلى Cython
EXCLUDE_FILES = ['setup.py', '__init__.py', 'manage.py', 'urls.py']
EXCLUDE_DIRS = ['migrations', '.venv', 'cythonizer']

# New exclusion lists for copying
EXCLUDE_COPYING_FILES = ['.env', '.gitignore', 'README.md']
EXCLUDE_COPYING_DIRS = ['logs', 'media', 'static', 'build', '.venv']

spinner = Spinner("Initializing")

def setup_logging():
    log_dir = 'log'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    log_file = os.path.join(log_dir, f'build_log_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt')
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    
    logger = logging.getLogger('build_logger')
    logger.setLevel(logging.INFO)
    logger.addHandler(file_handler)
    logger.propagate = False
    
    return logger

logger = setup_logging()

def should_exclude(file_path):
    file_name = os.path.basename(file_path)
    dir_name = os.path.basename(os.path.dirname(file_path))
    return file_name in EXCLUDE_FILES or dir_name in EXCLUDE_DIRS

def should_exclude_copying(file_path):
    file_name = os.path.basename(file_path)
    if file_name in EXCLUDE_COPYING_FILES:
        return True
    
    path_parts = file_path.split(os.path.sep)
    return any(excluded_dir in path_parts for excluded_dir in EXCLUDE_COPYING_DIRS)

def fix_cython_issues(file_path):
    with open(file_path, 'r') as file:
        content = file.read()
    
    # إصلاح مشكلة الفاصلة في الاستيراد
    content = re.sub(r'from (.*) import (.*),(.*)$', r'from \1 import \2\nfrom \1 import \3', content, flags=re.MULTILINE)
    
    with open(file_path, 'w') as file:
        file.write(content)
    logger.info(f"Fixed Cython issues in {file_path}")

def delete_python_files(directory, unconvertible_files):
    deleted_count = 0
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            if file.endswith('.py') and not should_exclude(file_path) and file_path not in unconvertible_files:
                os.remove(file_path)
                deleted_count += 1
                logger.info(f"Deleted {file_path}")
    logger.info(f"Total Python files deleted: {deleted_count}")

class CopyAndBuildCommand(Command):
    description = 'Copy project to build folder and convert to Cython'
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def capture_cython_errors(self, extension):
        error_output = io.StringIO()
        with contextlib.redirect_stderr(error_output):
            try:
                cythonize([extension], compiler_directives={'language_level': "3"}, quiet=True)
                return True, None
            except (CompileError, PyrexError) as e:
                return False, error_output.getvalue()

    def run(self):
        build_dir = 'build'
        unconvertible_files = []
        
        logger.info("Starting copy and build process for the entire project")
        
        spinner.start()

        spinner.update_message("Preparing build directory")
        time.sleep(1)
        if os.path.exists(build_dir):
            logger.info(f"Removing existing build directory: {build_dir}")
            shutil.rmtree(build_dir)
        
        spinner.update_message("Copying project files")
        time.sleep(1)
        logger.info(f"Copying project to {build_dir}")
        
        def custom_copy(src, dst):
            if should_exclude_copying(src):
                return
            if os.path.isdir(src):
                os.makedirs(dst, exist_ok=True)
                for item in os.listdir(src):
                    s = os.path.join(src, item)
                    d = os.path.join(dst, item)
                    custom_copy(s, d)
            else:
                shutil.copy2(src, dst)
        
        custom_copy('.', build_dir)
        
        spinner.update_message("Converting and compiling files")
        time.sleep(1)
        logger.info("Starting conversion and compilation of files")
        extensions = []
        conversion_count = 0
        for root, dirs, files in os.walk(build_dir):
            for file in files:
                if file.endswith('.py') and not should_exclude(os.path.join(root, file)):
                    py_file = os.path.join(root, file)
                    pyx_file = py_file.replace('.py', '.pyx')
                    try:
                        shutil.copy2(py_file, pyx_file)
                        fix_cython_issues(pyx_file)
                        module_name = os.path.relpath(pyx_file, build_dir).replace(os.path.sep, '.').replace('.pyx', '')
                        extension = Extension(module_name, [pyx_file])
                        
                        success, error_message = self.capture_cython_errors(extension)
                        if success:
                            extensions.append(extension)
                            conversion_count += 1
                            logger.info(f"Converted and compiled {py_file} to {pyx_file}")
                        else:
                            logger.error(f"Error compiling Cython file {pyx_file}:\n{error_message}")
                            os.remove(pyx_file)  # Remove the .pyx file
                            unconvertible_files.append(py_file)
                            logger.info(f"Keeping {py_file} as a Python file")
                    except Exception as e:
                        logger.error(f"Failed to process {py_file}: {str(e)}")
                        logger.error(traceback.format_exc())
                        unconvertible_files.append(py_file)
                        if os.path.exists(pyx_file):
                            os.remove(pyx_file)
        
        logger.info(f"Total files converted and compiled: {conversion_count}")
        logger.info(f"Total unconvertible files: {len(unconvertible_files)}")
        
        logger.info("Creating temporary distribution for building extensions")
        from distutils.dist import Distribution
        dist = Distribution({'ext_modules': extensions})
        
        logger.info("Building extensions")
        cmd = build_ext(dist)
        cmd.build_lib = build_dir
        cmd.ensure_finalized()
        
        logger.info("Running build_ext command")
        original_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')
        try:
            cmd.run()
        except Exception as e:
            sys.stdout = original_stdout
            logger.error(f"Build extensions process failed: {str(e)}")
            logger.error(traceback.format_exc())
            spinner.stop()
            print("Build process failed during extension building. Check the log for details.")
            return
        sys.stdout = original_stdout
        
        spinner.update_message("Cleaning up")
        time.sleep(1)
        logger.info("Deleting original Python files")
        delete_python_files(build_dir, unconvertible_files)
        
        logger.info("Copy and build process completed successfully")
        spinner.stop()
        print("Build process completed successfully.")
        if unconvertible_files:
            print(f"Note: {len(unconvertible_files)} files could not be converted to Cython and remain as Python files.")
            logger.info("Unconvertible files:")
            for file in unconvertible_files:
                logger.info(file)

setup_kwargs = {
    'name': "django_cython_project",
    'version': "0.1",
    'packages': find_packages(),
    'install_requires': [
        'Django>=3.2',
        'Cython>=0.29',
    ],
    'python_requires': '>=3.6',
    'include_package_data': True,
    'cmdclass': {
        'cbuild': CopyAndBuildCommand,
    },
}

if __name__ == "__main__":
    print("Setting up Django Cython project")
    logger.info("Starting Django Cython project setup")
    setup(**setup_kwargs)
    logger.info("Django Cython project setup completed")