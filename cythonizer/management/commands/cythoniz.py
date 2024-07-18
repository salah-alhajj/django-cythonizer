from django.core.management.base import BaseCommand
from cythonizer.build_tools import load_settings
from cythonizer.build_tools import  CopyAndBuildCommand
from setuptools import setup
from setuptools import  find_packages
from setuptools.dist import Distribution

class Command(BaseCommand):
    help = 'Set up and build the Django Cython project'

    def handle(self, *args, **options):
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
        self.stdout.write("Setting up Django Cython project")
        try:
            # Create a Distribution object
            dist = Distribution(setup_kwargs)
            
            # Initialize CopyAndBuildCommand with the Distribution object
            build_command = CopyAndBuildCommand(dist)
            
            # Set stdout and stderr if your CopyAndBuildCommand uses them
            build_command.stdout = self.stdout
            build_command.stderr = self.stderr
            
            # Run the command
            build_command.run()
            
            self.stdout.write(self.style.SUCCESS("Setup and build process completed"))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Setup and build process failed: {str(e)}"))