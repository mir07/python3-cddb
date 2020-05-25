import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="CDDB", # Replace with your own username
    version="0.1",
    author="Michael Rasmussen",
    author_email="mir@datanom.net",
    description="Python3 library interface to FreeDB",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mir07/python3-cddb",
    packages=setuptools.find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        'Intended Audience :: Developers',
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Multimedia :: Sound/Audio :: CD Audio :: CD Ripping",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ],
    python_requires='>=3.5',
)
