"""Setup script for finautapi-client package."""
import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="finautapi-client",
    version="0.1.0",
    author="Norsk Test AS",
    author_email="support@norsktest.no",
    description="Python client library for the FinAut API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/norsktest/finautapi-client",
    packages=setuptools.find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        "requests>=2.25.0",
        "python-dateutil>=2.8.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "pytest-cov>=2.10.0",
            "responses>=0.20.0",  # For mocking HTTP requests in tests
            "black>=21.0",
            "flake8>=3.9.0",
        ],
        "docs": [
            "sphinx>=3.0.0",
            "sphinx-rtd-theme>=0.5.0",
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/norsktest/finautapi-client/issues",
        "Source": "https://github.com/norsktest/finautapi-client",
        "Documentation": "https://finautapi-client.readthedocs.io",
    },
)