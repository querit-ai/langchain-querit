from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="langchain-querit",
    version="0.0.3",
    author="Querit.ai",
    author_email="support@querit.ai",
    description="A LangChain tool for Querit search functionality",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/querit-ai/langchain-querit",
    keywords=["langchain", "websearch", "querit", "search-tool"],
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.9",
    install_requires=[
        "langchain>=0.3",
        "pydantic>=2.0",
        "requests>=2.28.0",
        "python-dotenv>=1.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
            "types-requests",  # Type stubs for requests library
        ],
    },
    include_package_data=True,
)