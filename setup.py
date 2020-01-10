from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='pakkr',
    description='Pipeline utility library',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/zendesk/pakkr',
    version='0.1.0',
    license='Apache License 2.0',
    maintainer='Zendesk',
    maintainer_email='opensource@zendesk.com',
    packages=find_packages(exclude=['*_test.py', ]),
    classifiers=[
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Utilities'
    ],
    python_requires='>=3.6',
)
