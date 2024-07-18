import os
import glob

def delete_files(folder_path, extensions):
    """
    Delete all files with specified extensions in the given folder and its subfolders.
    
    :param folder_path: Path to the folder to clean
    :param extensions: List of file extensions to delete (e.g., ['.so', '.c', '.py.bak'])
    """
    for ext in extensions:
        pattern = os.path.join(folder_path, f'**/*{ext}')
        files = glob.glob(pattern, recursive=True)
        
        for file in files:
            try:
                os.remove(file)
                print(f"Deleted: {file}")
            except Exception as e:
                print(f"Error deleting {file}: {e}")

    print("Deletion process completed.")

# Specify the folder path and extensions
folder_to_clean = '/Users/slahaldynalhaj/Projects/django/build2'  # Replace with your folder path
extensions_to_delete = ['.so', '.c', '.pyx.bak']

# Run the deletion function
delete_files(folder_to_clean, extensions_to_delete)