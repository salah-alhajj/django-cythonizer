from setuptools import setup, find_packages
from build_tools.config import load_settings

settings = load_settings()

setup(
    name=settings['project']['name'],
    version=settings['project']['version'],
    packages=find_packages(where=settings['build']['path']),
    package_dir={'': settings['build']['path']},
    install_requires=settings['project']['install_requires'],
    python_requires=settings['project']['python_requires'],
    author=settings['project'].get('author', ''),
    author_email=settings['project'].get('author_email', ''),
    description=settings['project'].get('description', ''),
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url=settings['project'].get('url', ''),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)