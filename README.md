# VisualPIC - A Data Visualizer for PIC Codes

![VisualPIC logo](Logo/logo_horizontal.png)

## Introduction

VisualPIC is a new software for data visualization and analysis specifically designed for Particle-In-Cell simulation codes. In particular for PWFA and LWFA scenarios.

The main motivation that led to the creation of this application was the lack of a fast, simple and user-friendly visualization tool for PIC codes. 
For me, coming from the field of Computational Fluid Dynamics, where the simulation tools are much more mature, this was a big drawback.

Therefore, I dediced to develop this tool as a part of my PhD project in LWFA, so that instead of relying in countless (and probaly quite messy) 
MATLAB scripts for data analysis and visualization, I could implement everything in a single and easy to use software suite  that, hopefully, can be also be useful to many other people.

The main principles under which this application was developed are:

* Easyness of use (must have a graphical user interface).
* Cross-platform.
* Written in Python (and Qt for the interface).
* Open-source.
* Compatibility with multiple PIC codes.
* Open for collaboration.
* Modular design.

The code is currently still in its early stages and it only supports OSIRIS data, but it's being actively developed and collaborators are always welcome to join!

![VisualPIC Screnshot](Logo/VisualPIC.PNG)

## Installation
At this moment, the current version has only been tested on a Windows machine. Therefore, the installation instructions only apply tho this case, but the list of dependencies is the same for all OSs.

Initially, VisualPIC was developed to work on older Python (< 3.0) and Qt (< 5.0) versions. However, in order to add support for modern High DPI displays it was required to jump to Python 3.5 and Qt 5.7, together with the release candidate of Matplotlib 2.0.

### Required software
* Python 3.5.2 (other verions might also work).
* Qt 5.7 (will be installed with PyQt5).
* FFmpeg.

### Required Python packages
* Numpy.
* Matplotlib 2.0.0 RC 2 + custom backends.
* PyQt5.
* H5Py.
* Pillow.

### Windows Installation
* Install Python 3.5.2. Dowload [here](https://www.python.org/downloads/release/python-352/).
* Install PyQt5: `pip install pyqt5`.
* Install Pillow: `pip install pillow`.
* Install H5Py: `pip install h5py`.
* Download the Matplotlib 2.0.0 rc2 wheels for your Python version from [here](http://www.lfd.uci.edu/~gohlke/pythonlibs/#matplotlib)
* Once Matplotlib is installed, copy the custom backends found in the folder `VisualPIC/Custom Matplotlib Backends` into `[Your Python Path]\Lib\site-packages\matplotlib\backends`.
* Download FFmpeg ([link](https://ffmpeg.zeranoe.com/builds/)) and add it to your system PATH (As explained [here](http://www.wikihow.com/Install-FFmpeg-on-Windows), for example).
* After this, you should be able to run VisualPIC just by running the `__main__.py` file in the VisualPIC folder.


## Collaborating

### Adding support for more PIC codes

One of the main objectives when designing VisualPIC was that it should be able to read data from any code, but without adding more complexity to the main logic.

As a consequence, all the data reading process has been isolated from the rest of the code in well defined clases that read the data and "give it" to the rest of the code in a standarized way, independent from the simulation code that was used to create the data files.

For more details about this and on how to add compatibility for more simulation codes, see the [documentation](/Documentation/AddSupportForAnotherCode.md).
