from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="forex-trading-bot",
    version="0.1.0",
    author="Forex Trading Bot Contributors",
    description="Automated forex trading bot with mechanical strategy and strict risk management",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ttangina269-ai/forex-trading-bot",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "python-dateutil>=2.8.2",
        "pytz>=2023.3",
        "pyyaml>=6.0",
        "pydantic>=2.4.2",
        "numpy>=1.24.3",
        "pandas>=2.0.3",
        "scipy>=1.11.2",
        "v20>=20.30.0",
        "requests>=2.31.0",
        "python-dotenv>=1.0.0",
        "click>=8.1.7",
    ],
    entry_points={
        "console_scripts": [
            "forex-bot=src.main:cli",
        ],
    },
)
