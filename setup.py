from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name = 'lifestream',
    version = '0.0.10',
    description = 'The fastest way to make sense of a transaction log.',
    py_modules = ["lifestream"],
    package_dir = {'': 'src'},
    install_requires = [
        'pandas',
        'matplotlib',
        'numpy',
        'datetime'
    ],
    classifiers = [
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Intended Audience :: Information Technology",
        "Intended Audience :: Financial and Insurance Industry",
        "License :: OSI Approved :: MIT License",
        'Topic :: Office/Business',
        "Topic :: Office/Business :: Financial",
        "Topic :: Internet :: Log Analysis",
    ],
    long_description = long_description,
    long_description_content_type = "text/markdown",
    author = 'Jeff Withington',
    author_email = 'jeffrey.withington@gmail.com',
    url = 'https://github.com/invictus2010/lifestream'
) 