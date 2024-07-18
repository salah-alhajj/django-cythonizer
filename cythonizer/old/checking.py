import os
import sys
import json
from Cython.Build import cythonize

# قائمة بأسماء الملفات أو المجلدات التي يجب استثناؤها دائمًا
ALWAYS_EXCLUDE = ['__init__.py',  'manage.py',   'tests', 'migrations']

# أسماء شائعة للبيئات الافتراضية
VENV_NAMES = ['venv', 'env', '.venv', '.env', 'virtualenv']

def is_venv(path):
    """تحقق مما إذا كان المسار يشير إلى بيئة افتراضية"""
    return any(venv_name in path for venv_name in VENV_NAMES)

def analyze_project():
    convertible_files = []
    non_convertible_files = []
    non_convertible_folders = set()
    reasons = {}

    for root, dirs, files in os.walk(".", topdown=True):
        # تجاهل البيئات الافتراضية
        dirs[:] = [d for d in dirs if not is_venv(os.path.join(root, d))]

        if any(exclude in root for exclude in ALWAYS_EXCLUDE):
            non_convertible_folders.add(root)
            reasons[root] = "Excluded folder"
            continue

        for file in files:
            if file.endswith('.py'):
                full_path = os.path.join(root, file)
                relative_path = os.path.relpath(full_path)
                
                if any(exclude in relative_path for exclude in ALWAYS_EXCLUDE):
                    non_convertible_files.append(relative_path)
                    reasons[relative_path] = "Excluded by default"
                elif file.startswith('test_'):
                    non_convertible_files.append(relative_path)
                    reasons[relative_path] = "Test file"
                else:
                    convertible_files.append(relative_path)
    
    with open("convertible_files.json", "w") as f:
        json.dump(convertible_files, f, indent=2)
    
    with open("non_convertible_files.json", "w") as f:
        json.dump({
            "files": non_convertible_files,
            "folders": list(non_convertible_folders),
            "reasons": reasons
        }, f, indent=2)
    
    print(f"Convertible files: {len(convertible_files)}")
    print(f"Non-convertible files: {len(non_convertible_files)}")
    print(f"Non-convertible folders: {len(non_convertible_folders)}")

def convert_to_cython():
    with open("convertible_files.json", "r") as f:
        convertible_files = json.load(f)
    
    for file in convertible_files:
        cython_file = file.replace(".py", ".pyx")
        os.rename(file, cython_file)
    
    cythonize(convertible_files, compiler_directives={'language_level': "3"})

def check_conflicts():
    # Implement conflict checking logic here
    pass

def display_non_convertible():
    with open("non_convertible_files.json", "r") as f:
        data = json.load(f)
    
    print("\nNon-convertible folders:")
    for folder in data["folders"]:
        print(f"- {folder}: {data['reasons'].get(folder, 'No specific reason')}")

    print("\nNon-convertible files:")
    for file in data["files"]:
        print(f"- {file}: {data['reasons'].get(file, 'No specific reason')}")

if __name__ == "__main__":
    if sys.argv[1] == "analyze":
        analyze_project()
    elif sys.argv[1] == "convert":
        convert_to_cython()
    elif sys.argv[1] == "check-conflicts":
        check_conflicts()
    elif sys.argv[1] == "display-non-convertible":
        display_non_convertible()