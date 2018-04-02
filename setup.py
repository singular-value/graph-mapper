from setuptools import setup

with open('README.rst', 'r') as f:
    readme = f.read()

setup(name='graph_mapper',
      version='1.0.dev1',
      description='Uses graph partitioning techniques to assign data to locations on a rectangle',
      long_description=readme,
      url='http://github.com/singular-value/graph_mapper',
      author='Pranav Gokhale',
      author_email='pranavgokhale@uchicago.edu',
      license='MIT',
      packages=['graph_mapper'],
      install_requires=['metis'],
      python_requires='>=3',
      zip_safe=False)
