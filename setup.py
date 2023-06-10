# https://stackoverflow.com/questions/6323860/sibling-package-imports
# cd to directory of this file and activate conda environment
# then install with (note the dot at the of the line, it is required)
# pip install -e .

from setuptools import setup, find_packages

setup(name='AlgUtils', version='1.0', packages=find_packages())