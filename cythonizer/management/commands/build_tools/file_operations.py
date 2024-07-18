import os
import shutil
import re
from .config import EXCLUDE_FILES, EXCLUDE_DIRS, EXCLUDE_COPYING_FILES, EXCLUDE_COPYING_DIRS
from .logging_setup import logger

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