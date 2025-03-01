from setuptools import setup, find_packages

setup(
    name="ena",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "numpy>=1.21.0",
        "pandas>=1.3.0",
        "torch>=1.9.0",
        "transformers>=4.11.0",
        "scikit-learn>=0.24.2",
        "networkx>=2.6.3",
    ],
    author="Codeium AI",
    author_email="contact@codeium.ai",
    description="Enhanced NPC Autonomous System for AAA Games",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/codeium/ena",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8",
    ],
)
