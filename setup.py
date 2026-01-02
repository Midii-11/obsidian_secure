"""
Setup script for ObsidianSecure.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

setup(
    name="obsidian-secure",
    version="0.1.0",
    author="ObsidianSecure Contributors",
    description="Secure Obsidian Vault Encryption Tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(exclude=["tests", "examples"]),
    install_requires=[
        "cryptography>=42.0.0",
        "argon2-cffi>=23.1.0",
        "PySide6>=6.6.0",
        "watchdog>=4.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=8.0.0",
            "pytest-cov>=4.1.0",
            "black>=24.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "obsidian-secure=obsidian_secure.app:main",
        ],
    },
    python_requires=">=3.9",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Security :: Cryptography",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
    ],
)
