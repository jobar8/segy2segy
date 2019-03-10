from setuptools import setup, find_packages
setup(
    name="Segy2Segy",
    version="0.2",
    packages=find_packages(exclude=["tests*"]),
    scripts=['core/segy2segy.py'],

    install_requires=['gdal', 'obspy'],

    author="Joseph Barraud",
    author_email="joseph.barraud@gmail.com",
    description="A command line tool for projecting and transforming coordinates in SEGY files",
    license="BSD",
    keywords="segy sgy seismic projection",
    url="http://geophysicslabs.com",
)
