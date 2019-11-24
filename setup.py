from setuptools import setup

setup(name='dslogs',
      version='0.0.1',
      description='FRC Driver Station logs',
      url='http://github.com/jaustinpage/dslogs',
      author='Austin Page',
      author_email='',
      license='',
      packages=['dslogs'],
      install_requires=[
          'arrow',
          'dslogparser',
      ],
      zip_safe=False)
