from setuptools import setup

with open('README', 'r') as f:
    readme = f.read()

setup(name='data_mapper',
      version='0.1',
      description='Uses graph partitioning techniques to assign data to physical locations',
      long_description=readme,
      url='http://github.com/singular-value/data_mapper',
      author='Pranav Gokhale',
      author_email='pranavgokhale@uchicago.edu',
      license='MIT',
      packages=['data_mapper'],
      zip_safe=False)
