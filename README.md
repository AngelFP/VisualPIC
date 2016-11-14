# VisualPIC
Data visualizer for PIC codes.

![VisualPIC logo](Logo/logo.png)
![VisualPIC Screnshot](Logo/VisualPIC.PNG)

## Support for multiple PIC codes

VisualPIC is designed in a way that only a number of classes which are in direct contact with the 
data files (mainly the data readers) have to be modified or created in order to add compatibility 
for a new PIC code.

In the following simplified class diagram, these would be the dark gray classes plus the unit converter.
All of these classes read and process the data so that the rest of the VisualPIC code is independent of the
inner format of the data files.

![Class Diagram](Class Diagram/SimplifiedClassDiagram.png)

### Adding compatibility for another PIC code

As seen avobe, there are 4 classes that will have to be modified in order to add support for another PIC code, which are:

- FolderDataReader
- FieldReader
- RawDataReader
- UnitConverter

Before explaining the inner structure of each of these classes, let's explain in general terms how the data reading process works in VisualPIC:

One of the first things that has to be noticed is that there are 3 types of data (Fields, RawDataSets and RawDataTags). Let's explain each of them:

- Fields: By definition, a physical quantity that has a value for each point in space and time. This includes the components (x, y or z) of the electric and magnetic fields, the currents and, in some codes like OSIRIS, the charge density of a certain species.
- RawDataSets: We call Raw data to the macroparticle data. That is, data sets which contain the information of each macroparticle (position, momentum, charge, energy) so that a scatter or histogram plot can be made. It should be noted that one RawDataSet is created for each macroparticle variable (one for the x coordinate, another for the y coordinate, and so on), so usually we have around 7 or 8 data sets.
- RawDataTags: In some simulation codes, in order to allow particle tracking, it is possible to add a tag or label to each macroparticle. Since this information is not a physical quantity or anything that we want to plot, it is stored separately in the RawDataTags class.


