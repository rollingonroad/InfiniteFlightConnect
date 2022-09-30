from platform import python_version
import setuptools

with open('README.md', 'r') as fh:
    readme = fh.read()

setuptools.setup(
    name="ifcclient",
    version="0.0.1",
    author="David Wu",
    author_email="toffino@aliyun.com",
    description="Using python to connect the Infinite Flight Connect API v2.",
    long_description=readme,
    long_description_content_type="text/markdown",
    url="",
    include_package_data=False,
    package_data={},
    packages=setuptools.find_packages(),
    classifiers=[],
)