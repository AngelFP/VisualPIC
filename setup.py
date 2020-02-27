import sys
from setuptools import setup, find_packages

import VisualPIC

# Read long description
with open("README.md", "r") as fh:
    long_description = fh.read()

def read_requirements():
    with open('requirements.txt') as f:
        return [line.strip() for line in f.readlines()]

# Main setup command
setup(name='VisualPIC',
      version=VisualPIC.__version__,
      author='Angel Ferran Pousa',
      author_email="angel.ferran.pousa@desy.de",
      description='Data visualizer for PIC codes',
      long_description=long_description,
      long_description_content_type="text/markdown",
      url='https://github.com/AngelFP/VisualPIC',
      license='GPLv3',
      packages=find_packages('.'),
      package_data={'VisualPIC': ['ui/*',
                                  'Views/*.ui',
                                  'Assets/Visualizer3D/Colormaps/*.h5',
                                  'Assets/Visualizer3D/Opacities/*.h5',
                                  'Icons/*.png',
                                  'Icons/mpl/*.svg']},
      entry_points={
          'console_scripts': [
              'visualpic = VisualPIC.__main__:display_gui']},
      install_requires=read_requirements(),
      platforms='any',
      classifiers=(
          "Development Status :: 3 - Alpha",
          "Programming Language :: Python :: 3",
          "Programming Language :: Python :: 3.5",
          "Programming Language :: Python :: 3.6",
          "Intended Audience :: Science/Research",
          "Topic :: Scientific/Engineering :: Physics",
          "Topic :: Scientific/Engineering :: Visualization",
          "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
          "Operating System :: OS Independent"),
      )
