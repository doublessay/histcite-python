from setuptools import setup,find_packages

setup(
    name="histcite-python",
    author = "WangK2",
    author_email = "kw221225@gmail.com",
    version="0.1.1",
    description="A Python interface to histcite.",
    long_description = open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    keywords = ["histcite","web of science","citation network"],
    license="MIT",
    url="https://github.com/doublessay/histcite-python",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "pandas>=2.0",
        "pyarrow",
        "openpyxl"],
    
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={
        "console_scripts": [
            "histcite = histcite.cli:main",
        ]
    },

)