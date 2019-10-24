from setuptools import setup, find_packages


with open('README.md') as f:
    readme = f.read()


with open('LICENSE') as f:
    license = f.read()



setup(
    name='proco_game',
    version='0.0.1',
    description='A Game on Consumerism',
    long_description=readme,
    author='4chunato',
    url='https://github.com/4chunato/proco',
    license=license,
    package_data={'proco_game.data': ['*']},
    packages=find_packages(exclude=('tests', 'docs'))
)
