from platform import python_version
import setuptools
import os

about = {}
here = os.path.abspath(os.path.dirname(__file__))
print(here)
with open(os.path.join(here, "ifcclient", "__version__.py"), "r") as f:
    exec(f.read(), about)

with open('README.md', 'r') as fh:
    readme = fh.read()

setuptools.setup(
    name=about["__title__"],
    version=about["__version__"],
    author=about["__author__"],
    author_email=about["__author_email__"],
    description=about["__description__"],
    long_description=readme,
    long_description_content_type="text/markdown",
    url=about["__url__"],
    packages=["ifcclient"],
    include_package_data=True,
    package_data={"": ["LICENSE"]},
    license=about["__license__"],
    zip_safe=False,
    classifiers=[
        "License :: OSI Approved :: Apache Software License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
    ],
)