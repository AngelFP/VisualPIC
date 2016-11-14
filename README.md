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

### Structure of the data in VisualPIC

As seen above, there are 4 classes that will have to be modified in order to add support for another PIC code, which are:

- FolderDataReader
- FieldReader
- RawDataReader
- UnitConverter

Before explaining the inner structure of each of these classes, let's explain in general terms how the data reading process works in VisualPIC:

One of the first things that has to be noticed is that there are 3 types of data (Fields, RawDataSets and RawDataTags). Let's explain each of them:

- **Fields**: By definition, a physical quantity that has a value for each point in space and time. This includes the components (x, y or z) of the electric and magnetic fields, the currents and, in some codes like OSIRIS, the charge density of a certain species.
- **RawDataSets**: We call Raw data to the macroparticle data. That is, data sets which contain the information of each macroparticle (position, momentum, charge, energy) so that a scatter or histogram plot can be made. It should be noted that one RawDataSet is created for each macroparticle variable (one for the x coordinate, another for the y coordinate, and so on), so usually we have around 7 or 8 data sets.
- **RawDataTags**: In some simulation codes, in order to allow particle tracking, it is possible to add a tag or label to each macroparticle. Since this information is not a physical quantity or anything that we want to plot, it is stored separately in the RawDataTags class.

From these data sets, the RawDataTags and RawDataSets will always belong to a Species object. The fields can be independent from a species (e.g. electric and magnetic fields) or they can also belong to a particular species (e.g. charge density and current).

All these data objects are stored in the so-called DataContainer, where they are organized in just two lists: a list containing all the Species (which, at the same time, contain all the fields and RawData sets from that species) and another list containing al the Fields that do not belong to a particular species, the so-called "Domain Fields".

In order to create this data structure and read the data files there are three classes:

- **FolderDataReader**: This class is associated with the DataContainer and its main task is to scan the folder where all the data files are located. By doing so, it detects all the fields, raw data and species, and creates and adds all the corresponding objects (Species, Fields, RawDataSets and RawDataTags) to the DataContainer.
- **FieldReader** and **RawDataReader**: Two very similar classes whose function is kind of self-explanatory. Each field will condain a FieldReader, and each RawDataSet and RawDataTags will contain a RawDataReader. These readers know the inner structure of the data file, so that when we ask a Field or RawDataSet to return their data, they will call their inner data reader to perform the task.

### Adding compatibility for another PIC code

Now that we have a general idea of how the data is structured and what each class is doing, we can explain what do we have to modify to add compatibility for another code. Let's go class by class.

#### FolderDataReader

Location: VisualPIC/DataReading/folderDataReader.py

1. Detecting the simulation code and calling the right method.

In VisualPIC, the user has to indicate the location of the data folder (e.g. MS folder in the case of OSIRIS). Then when he clicks on "Load Data", VisualPIC detects which simulation code is the data from and calls the corresponding method to effectively load the data. At the moment, this is done based on the name of the simulation data folder because at least for Osiris and PIConGPU this is always called "MS" or "simOutput" respectively.

This is done in the "CreateCodeDictionaries" method. You have to add an entry to the self._codeName dictionary in the following way: 

```python
self._codeName = {"MS":"Osiris",
                  "simOutput":"PIConGPU",
			      "folderName":"myCodeName"} # <-- Line to add
```

Where "folderName" is the typical name of the simulation data folder created by your code, and "myCodeName" is the name of your simulation code.

Then, since every simulation software stores the data in a different way, a specific method for scanning the folder and loadind the data has to be created for each case, and VisualPIC will know which method to call depending on the detected simulation code name. This is also done by using a dictionary:

```python
self._loadDataFrom = {"Osiris": self.LoadOsirisData,
                        "PIConGPU":self.LoadPIConGPUData,
						"myCodeName": self.LoadMyCodeData} # <-- Line to add (method will be created later)
```

#### FieldReader

#### RawDataReader

#### UnitConverter
