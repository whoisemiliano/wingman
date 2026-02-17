#!/usr/bin/env python3
"""
Setup script for Wingman.
"""

from setuptools import setup, find_packages

# Read the README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="wingman",
    version="0.1.0",
    author="Emiliano Rodríguez",
    author_email="hi@whoisemiliano.dev",
    description="Your wingman for Salesforce—automate the boring admin tasks",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/whoisemiliano/wingman",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "wingman=wingman.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
