"""
Setup file for PlotScan
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
    name="PlotScan",
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
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    keywords="plot digitizer, plot to data",
    packages=["PlotScan"],
    install_requires=[
    "opencv-python",
    "numpy",
    "matplotlib",
    "paddlepaddle",
    "paddleocr"
    ],
    project_urls={
        "Bug Reports": "https://github.com/eftalgezer/PlotScan/issues",
        "Source": "https://github.com/eftalgezer/PlotScan",
        "Blog": "https://beyondthearistotelian.blogspot.com/search/label/PlotScan",
        "Developer": "https://www.eftalgezer.com/",
    },
    entry_points={
        "console_scripts": [
            "PlotScan = PlotScan.__main__:main",
        ]
    }
)
