import sys
from setuptools import setup, find_packages

def read_requirements():
    with open('requirements.txt') as f:
        return [line.strip() for line in f.readlines()]

# Main setup command
setup(name='VisualPIC',
      description='Data visualizer for PIC codes',
      url='https://github.com/AngelFP/VisualPIC',
      maintainer='Angel Ferran Pousa',
      license='GPL',
      packages=find_packages('.'),
      package_data={'VisualPIC': ['Views/*.ui',
                                  'Assets/Visualizer3D/Colormaps/*.h5',
                                  'Assets/Visualizer3D/Opacities/*.h5',
                                  'Icons/*.png',
                                  'Icons/mpl/*.svg']},
      entry_points={
          'console_scripts': [
              'visualpic = VisualPIC.__main__:display_gui']},
      install_requires=read_requirements(),
      platforms='any')
