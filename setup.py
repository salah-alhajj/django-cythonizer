from setuptools import setup, find_packages
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))
from cythonizer.build_tools  import load_settings

settings = load_settings()

setup(
    name=settings['project']['name'],
    version=settings['project']['version'],
    author="Salah Aldain Alhajj",
    author_email="contact@salahaldain.com",
    packages=find_packages(where=settings['build']['path']),
    package_dir={'': settings['build']['path']},
    install_requires=settings['project']['install_requires'],
    python_requires=settings['project']['python_requires'],
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