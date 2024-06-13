from setuptools import setup, find_packages

setup(
    name='DEBtoolPyIF',
    version='0.0.2',  # Increment this with new releases
    description='A Python Interface for the MATLAB package DEBtool, a package with tools for Dynamic Energy Budget models.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Diogo F. Oliveira',
    author_email='diogo.miguel.oliveira@tecnico.ulisboa.pt',
    url='https://github.com/diogo-f-oliveira/DEBtool-Python-Interface',  # Update with your GitHub URL
    license='MIT',
    packages=find_packages(),  # Automatically find packages in your project
    install_requires=[
        'numpy>=1.19.5',
        'pandas>=1.2.0',
        'tabulate>=0.8.0'
    ],  # List your package dependencies here
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
    ],
    python_requires='>=3.6',  # Specify Python version compatibility
)
