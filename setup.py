from setuptools import setup, find_packages

setup(
    name='your_package_name',
    version='0.1.0',
    author='Salah Aldain Alhajj',
    author_email='contact@salahaldain.com',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        'pyyaml',  # Include your dependencies here
    ],
    python_requires='>=3.6',  # Adjust according to your needs
    description='A brief description of your package',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://your-package-url.com',  # Your package URL
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
