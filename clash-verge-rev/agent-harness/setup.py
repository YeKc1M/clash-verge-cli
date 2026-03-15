"""
Setup script for cli-anything-clash-verge-rev package.
"""

import os
from setuptools import setup, find_namespace_packages

# Try to read README.md from different locations
readme_paths = ["README.md", "cli_anything/clash_verge_rev/README.md"]
long_description = "A complete CLI harness for Clash Verge Rev proxy client"
for path in readme_paths:
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as fh:
            long_description = fh.read()
        break

setup(
    name="cli-anything-clash-verge-rev",
    version="0.1.0",
    author="CLI Anything",
    author_email="cli-anything@example.com",
    description="A complete CLI harness for Clash Verge Rev proxy client",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/clash-verge-rev/clash-verge-rev",
    packages=find_namespace_packages(include=["cli_anything.*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: System Administrators",
        "Topic :: Internet :: Proxy Servers",
        "Topic :: System :: Networking",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "click>=8.0.0",
        "pyyaml>=6.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "mypy>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "cli-anything-clash-verge-rev=cli_anything.clash_verge_rev.clash_verge_rev_cli:main",
            "clash-verge-rev=cli_anything.clash_verge_rev.clash_verge_rev_cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
