# -*- coding: utf-8 -*-

#Copyright 2016 Ángel Ferran Pousa
#
#This file is part of VisualPIC.
#
#VisualPIC is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.
#
#VisualPIC is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with VisualPIC.  If not, see <http://www.gnu.org/licenses/>.

class Species:
    
    def __init__(self, name):
        self.name = name
        self.availableFields = list()
        self.customFields = list()
        self.rawDataSets = list()
        self.hasFields = False
        self.hasRawData = False
        
    def AddAvailableField(self,field):
        self.hasFields = True
        if field not in self.availableFields:
            self.availableFields.append(field)
        
    def AddCustomField(self, field):
        self.customFields.append(field)
            
    def AddRawDataSet(self, dataSet):
        self.hasRawData = True
        self.rawDataSets.append(dataSet)
        
    def HasFields(self):
        return self.hasFields
        
    def HasRawData(self):
        return self.hasRawData
            
    def GetFieldPlotData(self, fieldName, timeStep):
        for field in self.availableFields:
            if field.GetName() == fieldName:
                return field.GetPlotData(timeStep)
        
        for field in self.customFields:
            if field.GetName() == fieldName:
                return field.GetPlotData(timeStep)
    
    def GetRawDataSetPlotData(self, dataSetName, timeStep):
        for dataSet in self.rawDataSets:
            if dataSet.GetName() == dataSetName:
                return dataSet.GetPlotData(timeStep)
            
    def GetAvailableFieldNamesList(self):
        fieldNames = list()
        for field in self.availableFields:
            fieldNames.append(field.GetName())
        
        return fieldNames
        
    def GetCustomFieldNamesList(self):
        fieldNames = list()
        for field in self.customFields:
            fieldNames.append(field.GetName())
        return fieldNames
        
    def GetRawDataSetsNamesList(self):
        dataSetNames = list()
        for dataSet in self.rawDataSets:
            dataSetNames.append(dataSet.GetName())
        
        return dataSetNames
    
    def GetName(self):
        return self.name
    
    def GetField(self, fieldName):
        for field in self.availableFields:
            if field.GetName() == fieldName:
                return field
                
    def GetRawDataSet(self, dataSetName):
        for dataSet in self.rawDataSets:
            if dataSet.GetName() == dataSetName:
                return dataSet
        
    def LoadCustomFields(self):
        #to do
        #looks which fields are available and loads the custom fields that can be comuted from those
        raise Exception("notImplemented")
