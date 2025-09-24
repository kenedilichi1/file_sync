from setuptools import setup, find_packages
import os

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="localsync",
    version="2.0.0",
    author="LocalSync Team", 
    author_email="support@localsync.org",
    description="Easy file sharing over local network - No technical skills needed!",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Communications :: File Sharing",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[
        "cryptography>=3.4",
        "pyOpenSSL>=20.0",
    ],
    entry_points={
        "console_scripts": [
            "localsync=localsync.cli:main",
        ],
    },
    # Include additional files
    include_package_data=True,
    package_data={
        "localsync": ["*.md", "*.txt"],
    },
    # Friendly description for package indexes
    keywords="file-sharing easy simple local-network user-friendly",
    url="https://github.com/yourusername/localsync",
    project_urls={
        "Documentation": "https://github.com/yourusername/localsync/wiki",
        "Source": "https://github.com/yourusername/localsync",
        "Tracker": "https://github.com/yourusername/localsync/issues",
    },
)