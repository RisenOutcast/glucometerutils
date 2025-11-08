from setuptools import setup, find_packages

setup(
    packages=find_packages(),
    install_requires=[
        "freestyle-hid[encryption]>=1.1.0",
        "hidapi==0.14.0.post4"
    ],
)
