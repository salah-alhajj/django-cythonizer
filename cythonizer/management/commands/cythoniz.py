from django.core.management.base import BaseCommand



from build_tools.config import load_settings
from build_tools.build_command import CopyAndBuildCommand
from setuptools import setup, find_packages

class Command(BaseCommand):
    help = 'Set up the Django Cython project'

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
            setup(**setup_kwargs)
            CopyAndBuildCommand().run()  # Explicitly run the build command
            self.stdout.write(self.style.SUCCESS("Setup process completed"))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Setup process failed: {str(e)}"))