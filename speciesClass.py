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

from fieldClass import Field

class Species:
    
    def __init__(self, name):
        
        self.name = name
        self.availableFields = list()
        self.customFields = list()
        
    def AddAvailableField(self,field):
        
        if isinstance(field, Field):
            if field not in self.availableFields:
                self.availableFields.append(field)
        
    def AddCustomField(self, field):
        
        if isinstance(field, Field):
            self.customFields.append(field)
            
    def GetFieldPlotData(self, fieldName, timeStep):
        
        for field in self.availableFields:
            if field.GetName() == fieldName:
                return field.GetPlotData(timeStep)
        
        for field in self.customFields:
            if field.GetName() == fieldName:
                return field.GetPlotData(timeStep)
                
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
    
    def GetName(self):
        
        return self.name
    
    def GetField(self, fieldName):
        for field in self.availableFields:
            if field.GetName() == fieldName:
                return field
        
    def LoadCustomFields(self):
        #to do
        #looks which fields are available and loads the custom fields that can be comuted from those
        raise Exception("notImplemented")
