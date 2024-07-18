import os
import shutil
from typing import List
from typing import  Tuple

def rename_pyx_to_py(project_path: str) -> Tuple[List[str], List[str]]:
    """
    Rename all .pyx files to .py in the given project directory.
    
    Args:
    project_path (str): Path to the project directory.
    
    Returns:
    Tuple[List[str], List[str]]: A tuple containing two lists:
        - List of successfully renamed files
        - List of files that couldn't be renamed (if any)
    """
    renamed_files = []
    failed_files = []

    for root, _, files in os.walk(project_path):
        for file in files:
            if file.endswith('.pyx'):
                old_path = os.path.join(root, file)
                new_path = os.path.join(root, file[:-4] + '.py')
                
                try:
                    # Create a backup of the original file
                    backup_path = old_path + '.bak'
                    shutil.copy2(old_path, backup_path)
                    
                    # Rename the file
                    os.rename(old_path, new_path)
                    renamed_files.append(old_path)
                    
                    print(f"Renamed: {old_path} -> {new_path}")
                except Exception as e:
                    failed_files.append((old_path, str(e)))
                    print(f"Failed to rename {old_path}: {str(e)}")

    return renamed_files, failed_files

def undo_rename(renamed_files: List[str]) -> Tuple[List[str], List[str]]:
    """
    Undo the renaming process by restoring from .bak files.
    
    Args:
    renamed_files (List[str]): List of files that were renamed.
    
    Returns:
    Tuple[List[str], List[str]]: A tuple containing two lists:
        - List of successfully restored files
        - List of files that couldn't be restored (if any)
    """
    restored_files = []
    failed_restorations = []

    for old_path in renamed_files:
        backup_path = old_path + '.bak'
        current_py_path = old_path[:-4] + '.py'
        
        try:
            if os.path.exists(backup_path):
                os.remove(current_py_path)
                os.rename(backup_path, old_path)
                restored_files.append(old_path)
                print(f"Restored: {old_path}")
            else:
                raise FileNotFoundError(f"Backup file not found: {backup_path}")
        except Exception as e:
            failed_restorations.append((old_path, str(e)))
            print(f"Failed to restore {old_path}: {str(e)}")

    return restored_files, failed_restorations

if __name__ == "__main__":
    project_path = "/Users/slahaldynalhaj/Projects/django/build2"
    
    # Rename .pyx files to .py
    renamed, failed = rename_pyx_to_py(project_path)
    
    print("\nSummary:")
    print(f"Successfully renamed: {len(renamed)} files")
    print(f"Failed to rename: {len(failed)} files")
    
    if failed:
        print("\nFailed files:")
        for file, error in failed:
            print(f"  {file}: {error}")
    
    # Uncomment the following lines if you want to undo the renaming
    # print("\nUndoing renaming...")
    # restored, failed_restore = undo_rename(renamed)
    # print(f"Successfully restored: {len(restored)} files")
    # print(f"Failed to restore: {len(failed_restore)} files")