from setuptools import setup, find_packages

setup(
    name="dropbox-file-renamer",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "dropbox>=11.36.0",
        "python-dotenv>=1.0.0",
    ],
    entry_points={
        'console_scripts': [
            'dropbox-renamer=dropbox_renamer.rename_files_with_date:main',
        ],
    },
    author="Your Name",
    author_email="your.email@example.com",
    description="A script to download and rename Dropbox files with their modification dates",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/dropbox-file-renamer",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
) 