"""
Setup file for fstring_to_format
"""
from __future__ import absolute_import
from __future__ import with_statement
import os
from setuptools import setup
import io

HERE = os.getcwd().replace("{0}setup.py".format(os.sep), "")

LONG_DESCRIPTION = None

with io.open("{0}{1}README.md".format(HERE, os.sep), "r", encoding="utf-8") as readme:
    LONG_DESCRIPTION = readme.read()

setup(
    name="SimplePlotDigitizer",
    version="0.1.0",
    description="A Python command line utility to digitize plots in batch mode.",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    url="https://github.com/eftalgezer/fstring_to_format",
    author="Eftal Gezer",
    author_email="eftal.gezer@astrobiyoloji.org",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "Topic :: Education",
        "Topic :: Scientific/Engineering",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.1",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    keywords="plot digitizer, plot to data",
    packages=["plotdigitizer"],
    install_requires=[
    "opencv-python",
    "numpy",
    "matplotlib",
    "paddlepaddle",
    "paddleocr"
    ],
    project_urls={
        "Bug Reports": "https://github.com/eftalgezer/SimplePlotDigitizer/issues",
        "Source": "https://github.com/eftalgezer/SimplePlotDigitizer/",
        "Blog": "https://beyondthearistotelian.blogspot.com/search/label/SimplePlotDigitizer",
        "Developer": "https://www.eftalgezer.com/",
    },
)