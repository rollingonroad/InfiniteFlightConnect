from platform import python_version
import setuptools

with open('README.md', 'r') as fh:
    readme = fh.read()

setuptools.setup(
    name="ifcclient",
    version="0.0.4",
    author="David Wu",
    author_email="toffino@aliyun.com",
    description="Using python to connect the Infinite Flight Connect API v2.",
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://github.com/rollingonroad/InfiniteFlightConnect",
    include_package_data=False,
    package_data={},
    packages=setuptools.find_packages(),
    classifiers=[
        "License :: OSI Approved :: Apache Software License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
    ],
)