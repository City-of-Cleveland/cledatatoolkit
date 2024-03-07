<p align="center"><img src="branding/logo.svg"></img></p>

# cledatatoolkit
...is a library of tools published by the City of Cleveland's [Office of Urban Analytics & Innovation](https://www.clevelandohio.gov/city-hall/office-mayor/urban-ai) (Urban AI). The package is meant for civic data analysis using local, county and regional data sources. Many city datasets can be found using the City of Cleveland [Open Data Portal](https://data.clevelandohio.gov).

This package is divided into a series of modules. These modules can be used to perform a variety of functions, but are not necessarily related to one another. To learn more about what each module does, please visit the [Documentation](#documentation) section.

## Table of Contents
[Installation](#installation)  
[Overview](#overview)  
[Documentation](#documentation)   
[Additional Resources](#additional-resources)

## Installation
You can use `pip` in your terminal to install the package.
If you have difficulty installing on Linux (primarily Ubuntu) or macOS due to issues with the `arcgis` package (a dependency of this toolkit), you will likely need to install extra dependencies. For those operating systems, try first installing the Kerberos library via `sudo apt install libkrb5-dev` before using `pip` to install this package.
```
pip install cle-data-toolkit
```
This will also install the following dependencies:
* `geopandas`
* `pandas`
* `arcgis`
* `numpy`

We recommending installing into a [virtual environment](https://docs.python.org/3/library/venv.html) to not modify your base version of Python.

## Overview
This package contains several modules that perform a variety of functions including, but not limited to:
### ArcGIS Online API Helper Functions
* Extracting GeoDataFrames from ArcGIS Online FeatureLayers.
* Managing fields, features, and metadata within ArcGIS Online items.
### Spatial Helper Functions
* Apportioning: Allocating Census data to local boundaries that don't align
* Custom functions built on top of `geopandas` for more advanced spatial joins
    * Largest overlap
### County Property Data Enhancement
* Extracting insights from property owner names
* Standardizing property types and ownership

## Documentation
### Table of Contents
[`cledatatoolkit.ago_helpers`](#cledatatoolkitago_helpers-module) module
* [`FLCWrapper`](#cledatatoolkitago_helpersflcwrapperlayer_id-container_id-gis)  
    * [`add()`](#cledatatoolkitago_helpersflcwrapperaddschema-typelayer)
    * [`delete()`](#cledatatoolkitago_helpersflcwrapperdeleteid-typelayer)
    * [`get_layer()`](#cledatatoolkitago_helpersflcwrapperget_layerid)
    * [`get_layer_index()`](#cledatatoolkitago_helpersflcwrapperget_layer_indexname)
    * [`get_table()`](#cledatatoolkitago_helpersflcwrapperget_tableid)
    * [`get_table_index()`](#cledatatoolkitago_helpersflcwrapperget_table_indexname)
    * [`paste()`](#cledatatoolkitago_helpersflcwrapperpasteschema_id-layer_index)
    * [`update_container()`](#cledatatoolkitago_helpersflcwrapperupdate_container)
* [`FLWrapper`](#cledatatoolkitago_helpersflwrapperlayer_id-container_id-gis-howlayer)  
    * [`add_field()`](#cledatatoolkitago_helpersflwrapperadd_fieldfield_dict)
    * [`audit_fields()`](#cledatatoolkitago_helpersflwrapperaudit_fieldscolumns)
    * [`audit_schema()`](#cledatatoolkitago_helpersflwrapperaudit_schemadtypes)
    * [`delete_field()`](#cledatatoolkitago_helpersflwrapperdelete_fieldfield_name)
    * [`spatialize()`](#cledatatoolkitago_helpersflwrapperspatializeclausenone)
    * [`update()`](#cledatatoolkitago_helpersflwrapperupdateupdate_dict)
    * [`upsert()`](#cledatatoolkitago_helpersflwrapperupsertfs-id_field-batch_size0)

[`cledatatoolkit.census`](#cledatatoolkitcensus-module) module  
* ['calc_moe()'](#cledatatoolkitcensuscalc_moearray-howsum)  
`cledatatoolkit.property` module  
`cledatatoolkit.spatial` module

### `cledatatoolkit.ago_helpers` module

#### `cledatatoolkit.ago_helpers.FLCWrapper(layer_id, container_id, gis)`
>FLCWrapper stands for FeatureLayerCollection Wrapper. This is a class that contains various "quality of life" functions for working with the ArcGIS Online API, specifically FeatureLayerCollections. FeatureLayerCollections are FeatureServices that contain one or more FeatureLayers.

***Parameters:***
* `container_id` (*string*): The ArcGIS Online ID of the FeatureLayerCollection to which the `FLCWrapper` instance is based on. 
* `gis` (*arcgis.gis.GIS*): The GIS connection object to the ArcGIS REST API. This determines the context in which data can be retreived from ArcGIS Online. 

***Properties:***  
* `FLCWrapper.esriLookup` (*dictionary*): This is a dictionary that maps commonly used column types to specialized Esri field types. These field types are defined in the Service Definition of a FeatureService. This property is used in [`audit_schema()`](#cledatatoolkitago_helpersflwrapperaudit_schemadtypes) in the [`FLWrapper`](#cledatatoolkitago_helpersflwrapperlayer_id-container_id-gis-howlayer) class.
* `FLCWrapper.container` (*arcgis.features.FeatureLayerCollection*): This is the FeatureLayerCollection object from the ArcGIS Online REST API.
* `FLCWrapper.container_id` (*string*): This is the ArcGIS Online ID of the `FLCWrapper.container` object.
* `FLCWrapper.container_item` (*arcgis.gis.item*): This is the Item object from the ArcGIS Online REST API, which contains the `FLCWrapper.container` object.
* `FLCWrapper.gis` (*arcgis.gis.GIS*): This is the GIS connection object to the ArcGIS REST API. This determines the context in which data can be retreived from ArcGIS Online. 
* `FLCWrapper.sqlLookup` (*dictionary*): This is a dictionary that maps commonly used column types to specialized SQL field types. These field types are defined in the Service Definition of a FeatureService. This property is used in [`audit_schema()`](#cledatatoolkitago_helpersflwrapperaudit_schemadtypes) in the [`FLWrapper`](#cledatatoolkitago_helpersflwrapperlayer_id-container_id-gis-howlayer) class.

#### `cledatatoolkit.ago_helpers.FLCWrapper.add(schema, type='layer')`
>Add a new FeatureLayer to the FeatureLayerCollection.

***Parameters:***
* `schema` (*dictionary*): A dictionary of Service Definition properties that define the Layer or Table. 
* `type` (*string*): Either "layer" or "table". This determines the type of the FeatureLayer. Defaults to "layer".

***Raises:***  
* `Exception`: If the `type` parameter is neither "layer" nor "table".

***Returns:***  
* `arcgis.features.FeatureLayer`: An ArcGIS Online reference to the newly created Layer if `type` is set to "layer".
* `arcgis.features.Table`: An ArcGIS Online reference to the newly created Table if `type` is set to "table".

#### `cledatatoolkit.ago_helpers.FLCWrapper.delete(id, type='layer')`
>Delete a FeatureLayer from the FeatureLayerCollection.

***Parameters:***
* `id` (*integer*): ID of the Layer or Table to delete. (i.e 0, 1, 2, etc.)
* `type` (*string*): Either "layer" or "table". This determines the type of the FeatureLayer that is being deleted. Defaults to "layer".

***Raises:***  
* `Exception`: If the `type` parameter is neither "layer" nor "table".

***Returns:***  
* `None`

#### `cledatatoolkit.ago_helpers.FLCWrapper.get_layer(id)`
>Retreive a FeatureLayer from within the FeatureLayerCollection.

***Parameters:***
* `id` (*integer*): ID of the FeatureLayer within the FeatureLayerCollection. (i.e 0, 1, 2 etc.) 

***Returns:***  
* `arcgis.features.FeatureLayer`: The ArcGIS Online reference to the FeatureLayer.

#### `cledatatoolkit.ago_helpers.FLCWrapper.get_layer_index(name)`
>Get the index of a FeatureLayer within a FeatureLayerCollection.

***Parameters:***
* `name` (*string*): The name of FeatureLayer as defined in the Service Definition.

***Raises:***  
* `Exception`: If no results are found, an exception is raised.

***Returns:***  
* `integer`: If only one result is found, the numeric ID of the FeatureLayer that matches the `name` argument.
* `list`: If multiple results are found, a list of numeric IDs corresponding to all FeatureLayers that match the `name` argument.

#### `cledatatoolkit.ago_helpers.FLCWrapper.get_table(id)`
>Retreive a Table from within the FeatureLayerCollection.

***Parameters:***
* `id` (*integer*): ID of the Table within the FeatureLayerCollection. (i.e 0, 1, 2 etc.) 

***Returns:***  
* `arcgis.features.FeatureLayer`: The ArcGIS Online reference to the Table.

#### `cledatatoolkit.ago_helpers.FLCWrapper.get_table_index(name)`
>Get the index of a Table within a FeatureLayerCollection.

***Parameters:***
* `name` (*string*): The name of Table as defined in the Service Definition.

***Raises:***  
* `Exception`: If no results are found, an exception is raised.

***Returns:***  
* `integer`: If only one result is found, the numeric ID of the Table that matches the `name` argument.
* `list`: If multiple results are found, a list of numeric IDs corresponding to all Tables that match the `name` argument.

#### `cledatatoolkit.ago_helpers.FLCWrapper.paste(schema_id, layer_index)`
>This function will copy a Service Definition from a pre-existing ArcGIS Online FeatureLayer and append it to the FeatureLayerCollection as a new FeatureLayer without any Features. This function will only work for spatial Layers, Tables are not currently supported.

***Parameters:***
* `schema_id` (*string*): The ArcGIS Online ID of the FeatureLayerCollection reference that contains the FeatureLayer you want to paste.
* `layer_index` (*integer*): The numeric index of the FeatureLayer within the FeatureLayerCollection referenced in `schema_id`. (i.e 0, 1, 2 etc.)

***Returns:***  
* `arcgis.features.FeatureLayer`: An ArcGIS Online reference to the newly created FeatureLayer.

#### `cledatatoolkit.ago_helpers.FLCWrapper.update_container()`
>Refresh the connection to the FeatureLayerCollection.

***Returns:***  
* `None`

#### `cledatatoolkit.ago_helpers.FLWrapper(layer_id, container_id, gis, how='layer')`
>FLWrapper stands for FeatureLayer Wrapper. This is a class that contains various "quality of life" functions for working with the ArcGIS Online API, specifically FeatureLayers. FeatureLayers are individual layers contained within a FeatureLayerCollections. FeatureLayers can either be spatial 'layers' or nonspatial 'tables'. This wrapper supports both types.

***Extends*** [`cledatatoolkit.ago_helpers.FLCWrapper`](#cledatatoolkitago_helpersflcwrapperlayer_id-container_id-gis)  

***Parameters:***
* `layer_id` (*integer*): The ID of the Layer or Table within the FeatureLayerCollection. This is a number that often corresponds to the sequence of FeatureLayers within the collection.
* `container_id` (*string*): The ArcGIS Online ID of the FeatureLayerCollection to which the `FLWrapper` instance is based on. 
* `gis` (*arcgis.gis.GIS*): The GIS connection object to the ArcGIS REST API. This determines the context in which data can be retreived from ArcGIS Online.
* `how` (*string*): The type of FeatureLayer, either layer or table. Defaults to 'layer'.

***Properties:***  
* All properties contained in [`cledatatoolkit.ago_helpers.FLCWrapper`](#cledatatoolkitago_helpersflcwrapperlayer_id-container_id-gis).  
* `FLWrapper.crs` (*integer*): The EPSG ID of the FeatureLayer's coordinate reference system. This property defaults to `None` until the [`FLWrapper.spatialize()`](#cledatatoolkitago_helpersflwrapperspatializeclausenone) method is executed.
* `FLWrapper.fs` (*arcgis.features.FeatureSet*): An ArcGIS FeatureSet of the FeatureLayer. This property defaults to `None` until the [`FLWrapper.spatialize()`](#cledatatoolkitago_helpersflwrapperspatializeclausenone) method is executed.
* `FLWrapper.layer` (*arcgis.features.FeatureLayer* or *arcgis.features.Table*): A reference to the ArcGIS Online FeatureLayer object.
* `FLWrapper.layer_id` (*integer*): The numeric index of the FeatureLayer within the containing FeatureLayerCollection.
* `FLWrapper.gdf` (*geopandas.GeoDataFrame*): A GeoDataFrame based on the FeatureSet defined in `FLWrapper.fs`. This property defaults to `None` until the [`FLWrapper.spatialize()`](#cledatatoolkitago_helpersflwrapperspatializeclausenone) method is executed.
* `FLWrapper.sdf` (*pandas.DataFrame*): A Spatially Enabled Pandas DataFrame based on the FeatureSet defined in `FLWrapper.fs`. This property defaults to `None` until the [`FLWrapper.spatialize()`](#cledatatoolkitago_helpersflwrapperspatializeclausenone) method is executed.

#### `cledatatoolkit.ago_helpers.FLWrapper.add_field(field_dict)`
>Add a new field to the FeatureLayer.

***Parameters:***
* `field_dict` (*dictionary*): A dictionary of properties that define the field in the Service Definition, as outlined in the ArcGIS Online REST API.

***Returns:***  
* `None`

#### `cledatatoolkit.ago_helpers.FLWrapper.audit_fields(columns)`
>Compares an inputted list of column names to field names in the FeatureLayer. This is useful for comparing a DataFrame column names to fields in the Service Definition.

***Parameters:***
* `columns` (*list*): A list of field names. Could be from a pandas or PySpark DataFrame.

***Returns:***  
* `dictionary`: The key 'Only in FL' contains a list of fields that are only in the FeatureLayer, the key 'Not in FL' contains a list of fields that are only in the inputted list of column names.

#### `cledatatoolkit.ago_helpers.FLWrapper.audit_schema(dtypes)`
>Compares the FeatureLayer's Service Definition field schema to a list of data type tuples, usually sourced from a pandas or PySpark DataFrame using the dtypes method. This function will compare field schemas across the following three categories: name, type, and order.

***Parameters:***
* `dtypes` (*list*): A list of tuples, where the first element of the tuple is a field name and the second is the data type.

***Returns:***  
* `boolean`: If the order, types, and names of the `dtypes` parameter all match that of the FeatureLayer, `True` is returned. Otherwise `False` is returned.

#### `cledatatoolkit.ago_helpers.FLWrapper.delete_field(field_name)`
>Delete a field from the FeatureLayer.

***Parameters:***
* `field_name` (*string*): The name of the field to delete.

***Returns:***  
* `None`

#### `cledatatoolkit.ago_helpers.FLWrapper.spatialize(clause=None)`
>Query features from the FeatureLayer. This will initialize the Spatially Enabled DataFrame (`FLWrapper.sdf`) and FeatureSet (`FLWrapper.fs`). This function will also extract the Coordinate Reference System (`FLWrapper.crs`) and build a GeoDataFrame of the features (`FLWrapper.gdf`).

***Parameters:***
* `clause` (*string*): A SQL clause for filtering features. If None is inputted, the entire FeatureLayer is queried. Defaults to None.

***Returns:***  
* `None`

#### `cledatatoolkit.ago_helpers.FLWrapper.update(update_dict)`
>Update the FeatureLayer Service Definition.

***Parameters:***
* `update_dict` (*dictionary*): Dictionary of parameters to update in the definition.

***Returns:***  
* `None`

#### `cledatatoolkit.ago_helpers.FLWrapper.upsert(fs, id_field, batch_size=0)`
>This function will upsert features to the FeatureLayer based on a FeatureSet. This means new features will be added or existing features will be updated depending on whether or not the feature is already in the FeatureLayer.

***Parameters:***
* `fs` (*arcgis.features.FeatureSet*): A FeatureSet containing features to add and/or update.
* `id_field` (*string*): The field for which the upsert is performed. This field will be used to compare features from the inputted FeatureSet to features within the FeatureLayer.
* `batch_size` (*integer*): Recommended for larger datasets. The number of features to upsert per batch. After every batch the system will sleep for one second to avoid a timeout error. If zero the entire dataset will be uploaded in a single batch. Defaults to 0.

***Returns:***  
* `None`

### `cledatatoolkit.census` module

#### `cledatatoolkit.census.calc_moe(array, how='sum')`
>Helper function for developing margins of error (MOEs) for aggregations of sample estimates. This is recommended for when you are summing, or taking the proportion of multiple ACS estimates. This function implements the American Community Survey's documented methodology for calculating Margins of Error. To better understand how this process works, click [here](https://www.census.gov/content/dam/Census/library/publications/2018/acs/acs_general_handbook_2018_ch08.pdf).

***Parameters:***
* `array` (*list-like*): A list of margins of error to propogate over. If `how` = 'proportion', the arrays must be inputted as a 2-D array containing lists in the following order:
    1. The denominators of the proportion.
    2. The proportions themselves.
    3. The margins of error of the numerator.
    4. The margins of error of the denominator.
* `how` (*string*): Either 'sum' or 'proportion'. The aggregation methodology used for calculating the MOE. Defaults to 'sum'.

***Raises:***  
* `Exception`: If the `how` argument is not either 'sum' nor 'proportion', an exception is raised.

***Returns:***  
* `float`: The aggregated margin of error for the inputted array if `how`='sum'.
* `numpy.array`: The aggregated margins of error for the inputted array(s) if `how`='proportion'.

### `cledatatoolkit.property` module
### `cledatatoolkit.spatial` module
## Additional Resources
### Guide
See our tutorial notebook repo, [**open-data-examples**](https://github.com/City-of-Cleveland/open-data-examples), for curated tutorials of how you might use this package with Cleveland civic data sources!
