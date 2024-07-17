import ast
import os
import astroid
import logging
from typing import List, Dict, Tuple, Set

# إعداد التسجيل
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# القائمة الافتراضية للمجلدات المستبعدة
DEFAULT_EXCLUDED_DIRS = {
    'venv', 'env', '.venv', '.env', 'virtualenv',  # البيئات الافتراضية الشائعة
    '.git', '.github',  # مجلدات git
    '__pycache__', '.pytest_cache',  # ملفات الكاش
    'migrations',  # مجلدات الترحيل في Django
    'node_modules',  # مجلدات npm إذا كان المشروع يستخدم JavaScript
}

# القائمة الافتراضية للملفات غير القابلة للتحويل
DEFAULT_NON_CONVERTIBLE_FILES = {
    'urls.py',
    'settings.py',
    'wsgi.py',
    'asgi.py',
    'manage.py',
}

class AdvancedCompatibilityChecker:
    def __init__(self):
        self.incompatible_features = {
            'yield_from': self.check_yield_from,
            'async': self.check_async,
            'annotation': self.check_annotations,
            'metaclass': self.check_metaclass,
            'multiple_inheritance': self.check_multiple_inheritance,
            'dynamic_attributes': self.check_dynamic_attributes,
            'introspection': self.check_introspection,
            'eval_exec': self.check_eval_exec,
            'try_except_star': self.check_try_except_star,
        }

    def analyze_file(self, file_path: str) -> Dict[str, List[str]]:
        try:
            with open(file_path, 'r') as file:
                content = file.read()

            tree = ast.parse(content)
            astroid_tree = astroid.parse(content)

            incompatibilities = {}
            for feature, checker in self.incompatible_features.items():
                issues = checker(tree, astroid_tree)
                if issues:
                    incompatibilities[feature] = issues

            return incompatibilities
        except Exception as e:
            logger.error(f"Error analyzing {file_path}: {str(e)}")
            return {}

    def check_yield_from(self, tree: ast.AST, _) -> List[str]:
        issues = []
        for node in ast.walk(tree):
            if isinstance(node, ast.YieldFrom):
                issues.append(f"Line {node.lineno}: 'yield from' statement is not fully supported in Cython")
        return issues

    def check_async(self, tree: ast.AST, _) -> List[str]:
        issues = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.AsyncFunctionDef, ast.AsyncFor, ast.AsyncWith)):
                issues.append(f"Line {node.lineno}: Async/await syntax is not fully supported in Cython")
        return issues

    def check_annotations(self, tree: ast.AST, _) -> List[str]:
        issues = []
        for node in ast.walk(tree):
            if isinstance(node, ast.AnnAssign):
                issues.append(f"Line {node.lineno}: Type annotations may not be fully supported in Cython")
        return issues

    def check_metaclass(self, _, astroid_tree: astroid.Module) -> List[str]:
        issues = []
        for node in astroid_tree.nodes_of_class(astroid.ClassDef):
            if node.metaclass():
                issues.append(f"Line {node.lineno}: Metaclasses may not be fully supported in Cython")
        return issues

    def check_multiple_inheritance(self, _, astroid_tree: astroid.Module) -> List[str]:
        issues = []
        for node in astroid_tree.nodes_of_class(astroid.ClassDef):
            if len(node.bases) > 1:
                issues.append(f"Line {node.lineno}: Multiple inheritance may cause issues in Cython")
        return issues

    def check_dynamic_attributes(self, _, astroid_tree: astroid.Module) -> List[str]:
        issues = []
        for node in astroid_tree.nodes_of_class(astroid.ClassDef):
            if '__dict__' in node.locals:
                issues.append(f"Line {node.lineno}: Dynamic attribute creation may not work as expected in Cython")
        return issues

    def check_introspection(self, tree: ast.AST, _) -> List[str]:
        issues = []
        introspection_functions = ['globals', 'locals', 'vars', 'dir']
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                if node.func.id in introspection_functions:
                    issues.append(f"Line {node.lineno}: Introspection function '{node.func.id}' may not work as expected in Cython")
        return issues

    def check_eval_exec(self, tree: ast.AST, _) -> List[str]:
        issues = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                if node.func.id in ['eval', 'exec']:
                    issues.append(f"Line {node.lineno}: '{node.func.id}' function may not be supported in Cython")
        return issues

    def check_try_except_star(self, tree: ast.AST, _) -> List[str]:
        issues = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ExceptHandler) and node.type is None:
                issues.append(f"Line {node.lineno}: Bare 'except:' clause may behave differently in Cython")
        return issues

def analyze_project(project_path: str, excluded_dirs: Set[str] = DEFAULT_EXCLUDED_DIRS, non_convertible_files: Set[str] = DEFAULT_NON_CONVERTIBLE_FILES) -> Tuple[Dict[str, Dict[str, List[str]]], List[str], List[str]]:
    checker = AdvancedCompatibilityChecker()
    project_analysis = {}
    all_files = []
    non_convertible = []

    logger.info(f"Starting analysis of project at {project_path}")

    for root, dirs, files in os.walk(project_path):
        dirs[:] = [d for d in dirs if d not in excluded_dirs]

        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, project_path)
                all_files.append(relative_path)
                
                if file in non_convertible_files:
                    non_convertible.append(relative_path)
                else:
                    incompatibilities = checker.analyze_file(file_path)
                    if incompatibilities:
                        project_analysis[relative_path] = incompatibilities

    logger.info(f"Completed analysis. Found issues in {len(project_analysis)} files.")
    logger.info(f"Found {len(non_convertible)} non-convertible files.")
    return project_analysis, all_files, non_convertible

def generate_report(project_analysis: Dict[str, Dict[str, List[str]]], all_files: List[str], non_convertible: List[str]) -> str:
    report = "Cython Compatibility Analysis Report\n"
    report += "====================================\n\n"

    total_files = len(all_files)
    files_with_issues = len(project_analysis)
    non_convertible_count = len(non_convertible)
    report += f"Total Python files scanned: {total_files}\n"
    report += f"Files with compatibility issues: {files_with_issues}\n"
    report += f"Non-convertible files: {non_convertible_count}\n"
    report += f"Percentage of files with issues: {(files_with_issues / total_files) * 100:.2f}%\n\n"

    report += "Non-convertible Files:\n"
    report += "----------------------\n"
    for file in sorted(non_convertible):
        report += f"  - {file}\n"
    report += "\n"

    for file_path in sorted(all_files):
        report += f"File: {file_path}\n"
        report += "-" * (len(file_path) + 6) + "\n"
        
        if file_path in non_convertible:
            report += "  This file is non-convertible and will be excluded from Cython conversion.\n"
        elif file_path in project_analysis:
            incompatibilities = project_analysis[file_path]
            for feature, issues in incompatibilities.items():
                report += f"  {feature.capitalize()}:\n"
                for issue in issues:
                    report += f"    - {issue}\n"
        else:
            report += "  No compatibility issues found.\n"
        
        report += "\n"

    return report

if __name__ == "__main__":
    logger.info("Script started")
    project_path = "/Users/slahaldynalhaj/Projects/django/cython-lab"
    logger.info(f"Starting compatibility check for project: {project_path}")
    
    if not os.path.exists(project_path):
        logger.error(f"Project path does not exist: {project_path}")
    else:
        logger.info("Project path exists, starting analysis")
        
        custom_excluded_dirs = DEFAULT_EXCLUDED_DIRS.union({'custom_exclude_folder'})
        custom_non_convertible_files = DEFAULT_NON_CONVERTIBLE_FILES.union({'custom_non_convertible.py'})
        
        analysis, all_files, non_convertible = analyze_project(
            project_path, 
            excluded_dirs=custom_excluded_dirs,
            non_convertible_files=custom_non_convertible_files
        )
        logger.info("Analysis completed, generating report")
        report = generate_report(analysis, all_files, non_convertible)
        
        report_file = "cython_compatibility_report.txt"
        with open(report_file, "w") as f:
            f.write(report)
        logger.info(f"Report saved to {report_file}")

    logger.info("Compatibility check completed.")