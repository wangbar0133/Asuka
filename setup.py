from importlib.metadata import entry_points
from setuptools import setup, find_packages

with open("requirements.txt", "r") as f:
    requires = f.read().splitlines()

setup(
    name="Asuka",
    version="0.1.0",
    author="neicun",
    description="An extremely Fast Contract Defect Detectors",
    install_requires=requires,
    packages=find_packages(),
    entry_points={
        "console_scripts": ["asuka=core.__main__:main"]
    }
)