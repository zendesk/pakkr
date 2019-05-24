from setuptools import setup, find_packages

setup(
    name='Pakkr',
    description='Pipeline utility library',
    url='https://github.com/zendesk/pakkr',
    version='0.1.0.dev0',
    license='Apache License 2.0',
    maintainer='Zendesk',
    maintainer_email='opensource@zendesk.com',
    packages=find_packages(exclude=['*_test.py', ]),
    classifiers=[
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3.6',
        'Topic :: Utilities'
    ],
)
