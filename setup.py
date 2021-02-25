#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open('README.md') as readme_file:
    readme = readme_file.read()

requirements = [
    'psutil==5.8.0',
    'dataclasses_json==0.5.2',
    'click==7.1.2',
    'dataclasses==0.8',
    'python_dateutil==2.8.1',
]

setup_requirements = [ ]

test_requirements = [
    'pip==19.2.3',
    'bump2version==0.5.11',
    'wheel==0.33.6',
    'watchdog==0.9.0',
    'flake8==3.7.8',
    'tox==3.14.0',
    'coverage==4.5.4',
    'Sphinx==1.8.5',
    'twine==1.14.0',
    'psutil==5.8.0',
    'dataclasses_json==0.5.2',
    'click==7.1.2',
    'dataclasses==0.8',
    'python_dateutil==2.8.1',
]

setup(
    author="Xinyang Li",
    author_email='soybeanyoung@gmail.com',
    python_requires='>=3.5',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Gamers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description="A GUI helper for stacking pirates massacre missions in Elite: Dangerous",
    entry_points={
        'console_scripts': [
            'edmmc=edmmc.cli:main',
        ],
    },
    install_requires=requirements,
    license="MIT license",
    long_description=readme,
    long_description_content_type='text/markdown',
    include_package_data=True,
    keywords='edmmc',
    name='edmmc',
    packages=find_packages(include=['edmmc', 'edmmc.*']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/tautomer/EDMMC',
    version='0.1.0',
    zip_safe=False,
)
