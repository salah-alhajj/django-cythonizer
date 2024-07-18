from setuptools import setup, find_packages
from build_tools.config import load_settings
from build_tools.build_command import CopyAndBuildCommand

settings = load_settings()

setup_kwargs = {
    'name': settings['project']['name'],
    'version': settings['project']['version'],
    'packages': find_packages(),
    'install_requires': settings['project']['install_requires'],
    'python_requires': settings['project']['python_requires'],
    'include_package_data': True,
    'cmdclass': {
        'cbuild': CopyAndBuildCommand,
    },
}

if __name__ == "__main__":
    print("Setting up Django Cython project")
    setup(**setup_kwargs)
    print("Setup process completed")