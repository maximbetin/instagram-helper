"""Setup configuration for Instagram Updates."""

from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="instagram-updates",
    version="1.0.0",
    author="Maxim",
    author_email="",
    description="A tool that automatically fetches recent posts from Instagram accounts and generates HTML reports",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/maximbetin/instagram-updates",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: Internet :: WWW/HTTP :: Browsers",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=[],  # Let pyproject.toml handle dependencies
    entry_points={
        "console_scripts": [
            "instagram-updates=cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["templates/*.html"],
    },
    keywords="instagram scraper browser automation reports",
    project_urls={
        "Bug Reports": "https://github.com/maximbetin/instagram-updates/issues",
        "Source": "https://github.com/maximbetin/instagram-updates",
    },
)
