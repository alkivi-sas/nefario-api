from setuptools import setup

setup(
    name='nefario',
    packages=['nefario'],
    include_package_data=True,
    install_requires=[
        'flask',
        'redis',
        'Flask-HTTPAuth',
        'flask-cors',
        'flask_sqlalchemy',
        'Flask-Script',
        'flasgger',
        'salt-pepper',
    ],
)

