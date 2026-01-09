from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="shadowwatch",
    version="0.1.0",
    author="Tanishq",
    author_email="tanishq@shadowwatch.dev",
    description="Behavioral intelligence for your application - passive biometrics, fraud detection, personalization",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Tanishq1030/Shadow_Watch",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Security",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.9",
    install_requires=[
        "sqlalchemy>=2.0.0",
        "httpx>=0.25.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
        ],
    },
    keywords="behavioral biometrics fraud-detection security personalization fintech",
    project_urls={
        "Bug Reports": "https://github.com/Tanishq1030/Shadow_Watch/issues",
        "Source": "https://github.com/Tanishq1030/Shadow_Watch",
        "Documentation": "https://github.com/Tanishq1030/Shadow_Watch#readme",
    },
)
