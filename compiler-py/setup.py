from setuptools import setup, find_packages

setup(
    name="codegenz",
    version="1.1.0",
    description="Reference compiler for the CodeGenZ language",
    packages=find_packages(),
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "genz=genz.cli:main",
        ],
    },
)
