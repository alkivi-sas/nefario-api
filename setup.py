from setuptools import setup

setup(
    name='nefario',
    packages=['nefario'],
    include_package_data=True,
    install_requires=[
        'flake8',
        'flask',
        'pytest',
        'pytest-cov',
        'coverage',
        'redis',
        'salt-pepper',
    ],
)

