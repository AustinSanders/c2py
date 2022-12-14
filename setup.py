from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

setup(
    name='c2py',
    version='0.1.1',
    description="An event based self-adaptation framework",

    author='Austin Sanders',
    author_email="austin.sanders@nau.edu",
    license='MIT',

    classifiers=[
        'Development Status :: 2 - Pre-Alpha',

        'Intended Audience :: researchers',
        'Topic :: Software Architecture :: Self Adaptivity',

        'License :: MIT License',

        'Programming Language :: Python :: 3',
        ],

    keywords = 'Self adaptivity',

    package_dir={'c2py':'c2py'},
    packages=find_packages(),
    install_requires=[],
    )
