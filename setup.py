#!/usr/bin/env python3
import os
import sys

from setuptools import setup


def main():
    """The main entry point."""
    with open(os.path.join(os.path.dirname(__file__), 'README.md'), 'r') as f:
        readme = f.read()
    if sys.platform == "win32":
        scripts = ['scripts/runthis-server.bat']
    else:
        scripts = ['scripts/runthis-server']
    skw = dict(
        name='runthis-server',
        description='Safely serves multiple, isolated terminal sessions in a browser',
        long_description=readme,
        long_description_content_type='text/markdown',
        license='BSD',
        version='0.0.1',
        author='Anthony Scopatz',
        maintainer='Anthony Scopatz',
        author_email='scopatz@gmail.com',
        url='https://github.com/regro/runthis-server',
        platforms='Cross Platform',
        classifiers=['Programming Language :: Python :: 3'],
        packages=['runthis.server'],
        package_dir={'runthis.server': 'runthis/server'},
        package_data={'runthis.server': ['*.xsh']},
        scripts=scripts,
        install_requires=['ruamel.yaml', 'dataclasses', 'quart'],
        python_requires=">=3.6",
        zip_safe=False,
        )
    setup(**skw)


if __name__ == '__main__':
    main()
