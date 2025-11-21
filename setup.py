# setup.py
from setuptools import setup, find_packages

setup(
    name="digtool",
    version="1.0.0",
    description="DigTool - OSINT email presence checker",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "requests",
        "beautifulsoup4",
        "rich>=10.0.0"
    ],
    entry_points={
        "console_scripts": [
            "digtool=main:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License"
    ],
)
