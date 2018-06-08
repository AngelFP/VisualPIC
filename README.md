# VisualPIC - A Data Visualizer for PIC Codes

![VisualPIC logo](Logo/logo_horiz_transp.png)

## Introduction

VisualPIC is a new software for data visualization and analysis specifically designed to work with Particle-In-Cell (PIC) simulation codes, mainly for its application in plasma wakefield acceleration.

The original aim of VisualPIC was to provide a flexible and easy-to-use interface for data analysis, allowing the user to visualize the simulation results without having to write any code. This reduces the need of custom made scripts which, even if very efficient for specific cases, can easily tend to become quite cluttered and unpractical when used as the only tool for data visualization.

The main principles under which this application was developed are:

* Easyness of use (must have a graphical user interface).
* Cross-platform.
* Written in Python (and Qt for the interface).
* Open-source.
* Compatibility with multiple PIC codes.
* Open for collaboration.
* Modular design.

The main capabilities of the program include 2D and 3D visualization of fields and particle data, particle tracking through the simulation, the creation of snapshots and animations, as well as a dedicated visualizer for making eye-catching 3D renders of the simulation.

![VisualPIC Screnshot](Logo/VisualPIC.PNG)

## Installation
### Required software
* Python 3.5 or higher.
* Qt 5.7 or higher (will be installed with PyQt5).
* FFmpeg.

### Required Python packages
* Numpy.
* SciPy.
* Matplotlib.
* PyQt5.
* H5Py.
* Pillow.
* openPMD-viewer.

### Installating the easy way
* If you dont have it already, install Python 3.5 or higher. Download [here](https://www.python.org/downloads/release/python-352/). Choose the 64-bit version if possible.
* Open a terminal and simply type `pip install visualpic`.
* (Optional) Additionally, if you need to read data using the openPMD standard, install openPMD-Viewer by typing `pip install openPMD-viewer`.
* (Optional) If you plan on creating animations with VisualPIC, download FFmpeg ([link](https://ffmpeg.zeranoe.com/builds/)) and add it to your system PATH (As explained [here](http://www.wikihow.com/Install-FFmpeg-on-Windows), for example).

After this, you should be able to run VisualPIC by simply typing
```
visualpic
```
from the command line. (You do not need to be inside any specific folder for this.)

### Installating the manual way
* Install Python 3.5 or higher. Download [here](https://www.python.org/downloads/release/python-352/). Choose the 64-bit version if possible.
* Install all required dependencies: `pip install numpy, scipy, pyqt5, matplotlib, pillow, h5py, vtk`
* (Optional) For compatibility with codes using openPMD, install openPMD-viewer: `pip install openPMD-viewer`
* (Optional) If you plan on creating animations with VisualPIC, download FFmpeg ([link](https://ffmpeg.zeranoe.com/builds/)) and add it to your system PATH (As explained [here](http://www.wikihow.com/Install-FFmpeg-on-Windows), for example).
* Finally, install VisualPIC by cloning this repository and by typing:
```
python setup.py install
```

After this, you should be able to run VisualPIC by simply typing
```
visualpic
```
from the command line. (You do not need to be inside any specific folder for this.)


## Collaborating

### Adding support for more PIC codes

One of the main objectives when designing VisualPIC was that it should be able to read data from any code, but without adding more complexity to the main logic.

As a consequence, all the data reading process has been isolated from the rest of the code in well defined clases that read the data and "give it" to the rest of the code in a standarized way, independent from the simulation code that was used to create the data files.

For more details about this and on how to add compatibility for more simulation codes, see the [documentation](/Documentation/AddSupportForAnotherCode.md).

## Citing VisualPIC
If you use VisualPIC to produce plots or figures for any scientific work, please provide a reference to the following publication:

A. Ferran Pousa et al., *VisualPIC: A New Data Visualizer and Post-Processor for Particle-in-Cell Codes*, presented at IPAC’17, Copenhagen, Denmark, May 2017, paper TUPIK007.
