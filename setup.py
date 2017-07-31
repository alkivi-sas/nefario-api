from setuptools import setup

setup(
    name='nefario',
    packages=['nefario'],
    include_package_data=True,
    install_requires=[
        'flask',
        'redis',
        'salt-pepper',
    ],
)

