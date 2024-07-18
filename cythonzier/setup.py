import os
import sys
import shutil
import re
from setuptools import setup, find_packages, Command
from setuptools.extension import Extension
from Cython.Build import cythonize
from Cython.Distutils import build_ext

# قائمة الملفات والمجلدات التي يجب استثناؤها من التحويل إلى Cython
EXCLUDE_FILES = ['setup.py',  '__init__.py','manage.py','urls.py']
EXCLUDE_DIRS = ['migrations','.venv']

def should_exclude(file_path):
    file_name = os.path.basename(file_path)
    dir_name = os.path.basename(os.path.dirname(file_path))
    return file_name in EXCLUDE_FILES or dir_name in EXCLUDE_DIRS

def fix_cython_issues(file_path):
    with open(file_path, 'r') as file:
        content = file.read()
    
    # إصلاح مشكلة الفاصلة في الاستيراد
    content = re.sub(r'from (.*) import (.*),(.*)$', r'from \1 import \2\nfrom \1 import \3', content, flags=re.MULTILINE)
    
    with open(file_path, 'w') as file:
        file.write(content)

def delete_python_files(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py') and not should_exclude(os.path.join(root, file)):
                os.remove(os.path.join(root, file))
                print(f"Deleted {os.path.join(root, file)}")

class CopyAndBuildCommand(Command):
    description = 'Copy project to build folder and convert to Cython'
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        build_dir = 'build'
        
        print("Starting copy and build process for the entire project")
        
        if os.path.exists(build_dir):
            print("Removing existing build directory...")
            shutil.rmtree(build_dir)
        
        print(f"Copying project to {build_dir}...")
        shutil.copytree('.', build_dir, ignore=shutil.ignore_patterns('*.pyc', 'build', '.*', 'venv', 'env'))
        
        print("Converting .py files to .pyx...")
        extensions = []
        for root, dirs, files in os.walk(build_dir):
            for file in files:
                if file.endswith('.py') and not should_exclude(os.path.join(root, file)):
                    py_file = os.path.join(root, file)
                    pyx_file = py_file.replace('.py', '.pyx')
                    shutil.copy2(py_file, pyx_file)  # Copy instead of rename
                    print(f"Converted {py_file} to {pyx_file}")
                    fix_cython_issues(pyx_file)
                    module_name = os.path.relpath(pyx_file, build_dir).replace(os.path.sep, '.').replace('.pyx', '')
                    extensions.append(Extension(module_name, [pyx_file]))
        
        print("Compiling .pyx files...")
        ext_modules = cythonize(extensions, compiler_directives={'language_level': "3"})
        
        # Create a temporary distribution for building extensions
        from distutils.dist import Distribution
        dist = Distribution({'ext_modules': ext_modules})
        
        # Build extensions
        cmd = build_ext(dist)
        cmd.build_lib = build_dir
        cmd.ensure_finalized()
        cmd.run()
        
        print("Deleting Python files...")
        delete_python_files(build_dir)
        
        print("Copy and build process completed successfully.")

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
    setup(**setup_kwargs)
    print("Setup process completed.")