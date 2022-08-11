from setuptools import setup, find_packages, find_namespace_packages

setup(
    name="harf",
    version="0.0.1",
    description="Tools for modifying har files",
    author="Brendan DeLeeuw",
    packages= find_packages() + find_namespace_packages(),
    install_requires=[
        "Click",
        "pyserde",
    ],
    entry_points={
        "console_scripts": [
            "correlations = harf.cli:correlations"
        ],
    },
)
