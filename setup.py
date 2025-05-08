from setuptools import setup, find_packages

setup(
    name="python-log-analyzer",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "flask>=2.0.1",
        "pandas>=1.3.3",
        "numpy>=1.21.2",
        "python-dateutil>=2.8.2",
    ],
    entry_points={
        "console_scripts": [
            "log-analyzer=src.main:main",
        ],
    },
    author="jdbrewer",
    author_email="jdbrewer@protonmail.com",
    description="log analysis playground with a web interface",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/jdbrewer/python-log-analyzer",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    python_requires=">=3.7",
)