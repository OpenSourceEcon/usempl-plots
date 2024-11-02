from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as readme_file:
    longdesc = readme_file.read()

setup(
    name="usempl-plots",
    version="0.0.8",
    author="Richard W. Evans",
    license="CC0 1.0 Universal (CC0 1.0) Public Domain Dedication",
    description="Package for creating plots of US employment and unemployment",
    long_description=longdesc,
    long_description_content_type="text/markdown",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: Developers",
        "License :: CC0 1.0 Universal (CC0 1.0) Public Domain Dedication",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="Data analysis visualization tools US employment unemployment",
    url="https://github.com/OpenSourceEcon/usempl-plots",
    download_url="https://github.com/OpenSourceEcon/usempl-plots",
    project_urls={
        "Issue Tracker": "https://github.com/OpenSourceEcon/usempl-plots/issues",
    },
    packages=find_packages(),
    package_data={"usempl_plots": ["data/*"]},
    include_packages=True,
    python_requires=">=3.12",
    install_requires=[
        "numpy>=1.23.4",
        "scipy>=1.9.3",
        "pandas>=1.5.2",
        "pandas-datareader>=0.10.0",
        "bokeh>=3.0",
        "matplotlib",
        "pytest>=7.1.2",
        "pytest-cov",
        "coverage>=6.3.2",
        "codecov>=2.1.11",
        "black>=24.1.1",
        "pip>=22.3.1",
        "linecheck>=0.1.0",
    ],
    tests_require=["pytest"],
)
