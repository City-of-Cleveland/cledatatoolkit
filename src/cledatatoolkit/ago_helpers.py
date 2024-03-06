import pandas as pd
import geopandas as gpd
import numpy as np

from time import sleep

from arcgis.gis import GIS
from arcgis.features import managers
from arcgis.features import FeatureSet
from arcgis.features import FeatureLayer
from arcgis.features import FeatureLayerCollection

#Dictionary for looking up delta types to esri types.
esriLookup = {
    'string':'esriFieldTypeString',
    'double':'esriFieldTypeDouble',
    'decimal(15,2)':'esriFieldTypeDouble',
    'decimal(10,0)':'esriFieldTypeDouble',
    'date':'esriFieldTypeDate',
    'timestamp':'esriFieldTypeDate',
    'int':'esriFieldTypeInteger',
    'bigint':'esriFieldTypeInteger'
}
#Develop a similar lookup for sqltypes
sqlLookup = {
    'string':'sqlTypeNVarchar',
    'double':'sqlTypeDouble',
    'decimal(15,2)':'sqlTypeDouble',
    'decimal(10,0)':'esriFieldTypeDouble',
    'date':'sqlTypeTimestamp2',
    'timestamp':'sqlTypeTimestamp2',
    'int':'sqlTypeInteger',
    'bigint':'esriFieldTypeInteger'
}


class FLCWrapper:

    def __init__(self, container_id, gis):
        """FLCWrapper stands for FeatureLayerCollection Wrapper. 
        This is a class that contains various "quality of life" functions for working with the ArcGIS Online API, specifically FeatureLayerCollections.
        FeatureLayerCollections are FeatureServices that contain one or more FeatureLayers.

        Args:
            container_id (str): The ArcGIS Online ID of the FeatureLayerCollection to which you want to connect.
            gis (GIS): The GIS connection object, generated using the ArcGIS API.
        """
        self.gis = gis
        self.container_id = container_id
        self.container_item = gis.content.get(container_id)
        self.container=FeatureLayerCollection.fromitem(self.container_item)
        #Add esriLookup and sqlLookup for internal use functions
        self.esriLookup = esriLookup
        self.sqlLookup = sqlLookup

    def update_container(self):
        """Refresh the connection to the FeatureLayerCollection.
        """
        self.container_item = self.gis.content.get(self.container_id)
        self.container=FeatureLayerCollection.fromitem(self.container_item)


    def get_layer(self, id:int):
        """Retreive a FeatureLayer from within the FeatureLayerCollection.

        Args:
            id (int): ID of the FeatureLayer within the FeatureLayerCollection. (i.e 0, 1, 2 etc.)

        Returns:
            FeatureLayer: The ArcGIS Online reference to the FeatureLayer.
        """
        self.update_container()
        fl = [a for a in self.container.layers if str(a.properties.id) == str(id)][0]
        return fl
    
    def get_table(self, id:int):
        """Retreive a Table from within the FeatureLayerCollection.

        Args:
            id (int): ID of the Table within the FeatureLayerCollection. (i.e 0, 1, 2 etc.) 

        Returns:
            FeatureLayer: The ArcGIS Online reference to the Table.
        """
        self.update_container()
        fl = [a for a in self.container.tables if str(a.properties.id) == str(id)][0]
        return fl
    
    def get_layer_index(self, name:str):
        """Get the index of a FeatureLayer within a FeatureLayerCollection.

        Args:
            name (str): The name of FeatureLayer as defined in the Service Definition.

        Raises:
            Exception: If no results are found, an exception is raised.

        Returns:
            int: If only one result is found, the numeric ID of the FeatureLayer that matches the `name` argument.
            list: If multiple results are found, a list of numeric IDs corresponding to all FeatureLayers that match the `name` argument.
        """
        self.update_container()
        #Get list of IDs by name
        ids = [a.properties.id for a in self.container.layers if a.properties.name==name]
        #Return cases
        if len(ids) == 1:
            return ids[0]
        
        elif len(ids) > 1:
            return ids
        
        else:
            raise Exception("name does not match any FeatureLayer names in FeatureLayerCollection")

    def get_table_index(self, name:str):
        """Get the index of a Table within a FeatureLayerCollection.

        Args:
            name (str): The name of Table as defined in the Service Definition.

        Raises:
            Exception: If no results are found, an exception is raised.

        Returns:
            int: If only one result is found, the numeric ID of the Table that matches the `name` argument.
            list: If multiple results are found, a list of numeric IDs corresponding to all Tables that match the `name` argument.
        """
        self.update_container()
        #Get list of IDs by name
        ids = [a.properties.id for a in self.container.tables if a.properties.name==name]
        #Return cases
        if len(ids) == 1:
            return ids[0]
        
        elif len(ids) > 1:
            return ids
        
        else:
            raise Exception("name does not match any Table names in FeatureLayerCollection")
        

    def paste(self, schema_id, layer_index):
        """This function will copy a Service Definition from a pre-existing ArcGIS Online FeatureLayer and append it to the FeatureLayerCollection as a new FeatureLayer without any Features. 
        This function will only work for FeatureLayers, Tables are not currently supported.

        Args:
            schema_id (str): The ArcGIS Online ID of the FeatureLayerCollection reference that contains the FeatureLayer you want to paste.
            layer_index (int): The numeric index of the FeatureLayer within the FeatureLayerCollection referenced in `schema_id`. (i.e 0, 1, 2 etc.)

        Returns:
            FeatureLayer: An ArcGIS Online reference to the newly created FeatureLayer.
        """

        schema_fl = self.gis.content.get(schema_id).layers[layer_index]

        #Since ESRI likes to make their own little fun datatypes, we have to convert the layer definition to a dictionary
        schema_properties = dict(schema_fl.properties)
        #We also have to delete the 'indexes' key:value pair since our layer will not need any pre-defined statistics or insights
        del schema_properties['indexes']
        #The index value is set to the nth layer that is being added

        #Add the new layer to the container
        self.container.manager.add_to_definition(json_dict = {'layers':[schema_properties]})
        self.update_container()

        #Return the new FeatureLayer
        return self.container.layers[-1]
    

    def add(self, schema:dict, type:str="layer"):
        """Add a new FeatureLayer or Table to the FeatureLayerCollection.
        Args:
            schema (dict): A dictionary of Service Definition properties that define the FeatureLayer or Table.
            type (str): Either "layer" or "table". This determines the type of the Service Definition. Defaults to "layer".

        Raises:
            Exception: If the type parameter is neither "layer" nor "table".

        Returns:
            FeatureLayerCollection: An ArcGIS Online reference to the newly created FeatureLayer if `type` is set to "layer".
            Table: An ArcGIS Online reference to the newly created Table if `type` is set to "table".
        """
        #If the type is table
        if type.lower() == 'table':
            #Add the new table to the container
            self.container.manager.add_to_definition(json_dict = {'tables':[schema]})
            self.update_container()
            return self.container.tables[-1]
        
        #If the type is layer
        elif type.lower() == 'layer':
            #Add the new layer to the container
            self.container.manager.add_to_definition(json_dict = {'layers':[schema]})
            self.update_container()
            return self.container.layers[-1]
        
        else:
            raise Exception('You need to identify a `type` of "layer" or "table".')
        

    def delete(self, id:int, type:str="layer"):
        """Delete a FeatureLayer or Table from the FeatureLayerCollection.

        Args:
            id (int): ID of the FeatureLayer or Table to delete (i.e 0, 1, 2, etc.).
            type (str): Either "layer" or "table". This determines the type of Service Definition component that is being deleted. Defaults to "layer".

        Raises:
            Exception: If the type parameter is neither "layer" nor "table".
        """

        #Construct delete dict depending on type.
        if type.lower() == 'layer':
            delete_dict = {"layers":[
                {"id":id}
            ]}

        elif type.lower() == 'table':
            delete_dict = {"tables":[
                {"id":id}
            ]}

        #Otherwise throw an error.
        else:
            raise Exception('You need to identify a `type` of "layer" or "table".')
            
        #Delete the layer from definition
        self.container.manager.delete_from_definition(delete_dict)
        self.update_container()


class FLWrapper(FLCWrapper):

    def __init__(self, layer_id, container_id, gis, how='layer'):
        """FLCWrapper stands for FeatureLayer Wrapper. 
        This is a class that contains various "quality of life" functions for working with the ArcGIS Online API, specifically FeatureLayers.
        FeatureLayers are individual layers contained within a FeatureLayerCollections.

        Args:
            layer_id (int): The ID of the FeatureLayer within the FeatureLayerCollection. This is a number that often corresponds to the sequence of FeatureLayers within the collection.
            container_id (str): The ID of the FeatureLayerCollection that contains the FeatureLayer.
            gis (GIS): The GIS connection object, generated using the ArcGIS API.
            how (str, optional): The type of FeatureLayer, either layer or table. Defaults to 'layer'.
        """

        super().__init__(container_id, gis)

        self.layer_id = layer_id
        #If the FLWrapper points to a layer
        if how.lower()=="layer":
            self.layer = self.get_layer(self.layer_id)

        elif how.lower()=="table":
            self.layer = self.get_table(self.layer_id)

    def spatialize(self, clause=None):
        """Query features from the FeatureLayer. 
        This will initialize the Spatially Enabled DataFrame (self.sdf) and FeatureSet (self.fs).
        This function will also extract the Coordinate Reference System (self.crs) and build a GeoDataFrame of the features (self.gdf)

        Args:
            clause (str, optional): SQL clause for filtering features. Defaults to None.
        """

        if clause != None:
            self.fs = self.layer.query(where=clause)

        else:
            self.fs = self.layer.query()

        #Get Spatially Enabled Dataframe
        self.sdf = self.fs.sdf
        #Get CRS
        self.crs = self.fs.spatial_reference['latestWkid']
        #Build GeoDataFrame
        geojson = self.fs.to_json
        self.gdf = gpd.read_file(geojson).set_crs(self.crs)
        self.gdf['geometry'] = self.gdf.make_valid()


    def add_field(self, field_dict:dict):
        """Add a new field to the FeatureLayer

        Args:
            field_dict (dict): Dictionary of properties to add to the field.
        """
        update_dict = {'fields':[field_dict]}
        self.layer.manager.add_to_definition(update_dict)
    
    def delete_field(self, field_name:str):
        """Delete a field from the FeatureLayer

        Args:
            field_name (str): Name of the field to delete
        """
        delete_dict = {
            'fields':[{'name':field_name}]
        }
        self.layer.manager.delete_from_definition(delete_dict)
        
    def audit_fields(self, columns):
        """Compares fields in a delta table and fields in an ArcGIS FeatureLayer.

        Args:
            columns (list): A list of field names. Could be from a pandas or PySpark DataFrame.

        Returns:
            dict: The key 'Only in FL' contains a list of fields that are only in the FeatureLayer, the key 'Not in FL' contains a list of fields that are only in the Delta table.
        """
        #Get list of fields
        fl_fields = [a['name'] for a in self.layer.properties['fields']]
        #Get list of fields to delete
        delete = [a for a in fl_fields if a not in columns and a.lower() != 'objectid']
        add = [a for a in columns if a not in fl_fields and a.lower() != 'objectid']

        return {'Only in FL':delete, 'Not in FL':add}
    
    def audit_schema(self, dtypes):
        """Compares the service definition field schema to a list of data type tuples, usually from df.dtypes. 

        Args:
            dtypes (list): A list of tupes, where the first element of the tuple is a field name and the second is the data type.

        Returns:
            bool: The function compares schema on the basis of field name, type, and order. If any of these criteria do not match, False is returned. Otherwise True is returned.
        """
        result = None
        #These fields are not included in the comparison
        excluded_fs_fields = ['OBJECTID','SHAPE__AREA','SHAPE__LENGTH','GLOBALID']
        #Represent the feature service definition as a list of tuples showing the name and type.
        fs_schema = [(a['name'],a['type']) for a in self.layer.properties['fields'] if a['name'].upper() not in excluded_fs_fields]
        #Do the same thing for the inputted dtypes
        column_schema = [(a[0],self.esriLookup[a[1]]) for a in dtypes]
        #Return if they match or not
        result = fs_schema == column_schema
        return result

    def update(self, update_dict:dict):
        """Update the FeatureLayer service definition.

        Args:
            update_dict (dict): Dictionary of parameters to update in the definition.
        """
        self.layer.manager.update_definition(update_dict)
    
    def upsert(self, fs, id_field, batch_size=0):
        """Upserts features to a FeatureLayer.

        Args:
            fs (FeatureSet): FeatureSet of features to add.
            id_field (str): ID Field for which the Upsert is performed.
            batch_size (int): For larger datasets, the number of features to upsert per batch. After every batch the system will sleep for one second to avoid a timeout error. If zero the entire dataset will be uploaded in a single batch.
        """
        #Coerce featureset to pandas dataframe
        df = fs.sdf.set_index(id_field)
        
        oid = self.layer.properties.objectIdField
        #Coerce to layer Pandas DataFrame and get the id_field, if the column doesn't exist, return an empty series.
        #Furthermore, since OBJECTIDs might not match between dataframes, we need to crosswalk between the OBJECTID field and the id_field identified in the function.
        try:
            indices = self.layer.query().sdf[[oid,id_field]].set_index(id_field)
            #Update OBJECTID from FeatureSet to match OBJECTID from current FeatureLayer
            df.loc[:,oid] = indices[oid]
        except KeyError:
            indices = pd.Series()

        #Helper function for determing adds and updates
        def partition(df):

            #Get features to add and features to update and features to delete
            try:
                to_add = FeatureSet.from_dataframe(df.copy()[df[id_field].isin(indices.index) == False])
            except KeyError:
                to_add = None
            try:    
                to_update = FeatureSet.from_dataframe(df.copy()[df[id_field].isin(indices.index)])
            except KeyError:
                to_update = None

            return to_add, to_update

        #Drop index
        df.reset_index(inplace=True)

        if batch_size > 0:

            batches = df.shape[0] / batch_size

            #For every batch
            for batch in np.array_split(df, batches):
                #Break it up into adds and updates
                to_add, to_update = partition(batch)
                #Add to feature service
                self.layer.edit_features(adds=to_add, updates=to_update)
                #Sleep for one second to avoid timeout
                sleep(1)
        
        else:
            #Get all adds and updates for the guy
            to_add, to_update = partition(df)
            #Upsert FeatureSet
            self.layer.edit_features(adds=to_add, updates=to_update)
