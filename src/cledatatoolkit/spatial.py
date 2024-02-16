import geopandas as gpd
import pandas as pd
import numpy as np

from .census import calc_moe

# Largest overlap function 1:1 take the biggest overlapping feature
def largest_overlap(
    target_gdf: gpd.GeoDataFrame,
    target_key: str,
    join_gdf: gpd.GeoDataFrame,
    transfer_field: str,
    new_name: str,
    data_type: str = "string",
    fix_missing=False,
    reference_field="par_city",
    reference_value: str = "CLEVELAND",
):
    """Spatial join of the largest overlap between polygons

    Args:
        target_gdf (GeoDataFrame): GeoDataFrame on left
        target_key (str): Column name
        join_gdf (GeoDataFrame): GeoDataFrame on right
        transfer_field (str): The column you are interested in adding
        new_name (str): Renaming that transfer field
        data_type (str, optional): What to cast the value as. Defaults to "string".
                                'string' for best performance
                                'float64' for float
                                'int64' for integer

    Returns:
        gpd.GeoDataFrame
    """
    # set up new column name based on function parameter
    new_column = f"{new_name}"

    # Formatting the outputs
    # If you want an integer represented as a string without decimal points
    if data_type == "int_string":
        join_gdf[transfer_field] = (
            join_gdf[transfer_field].astype("Int64").astype("string")
        )
    else:
        join_gdf[transfer_field] = join_gdf[transfer_field].astype(data_type)

    # Intersect two layers
    intersect_gdf = gpd.overlay(target_gdf, join_gdf, how="intersection")

    # Generate the sq footage of each intersecting area
    intersect_gdf["sqft_area"] = intersect_gdf.geometry.area

    # Sort by square feet, drop all of each parcel number group except the largest overlap, drop area column
    intersect_gdf = intersect_gdf.sort_values(by='sqft_area').drop_duplicates(
        subset=target_key, keep='last').drop('sqft_area', axis=1)

    new_gdf = target_gdf.merge(intersect_gdf[[target_key, transfer_field]], 'left', on=target_key).rename(
        columns={transfer_field: new_column})

    # Fix sjoins that failed to match but must be filled by definition
    # e.g. Cleveland parcels that have no neighborhoods assigned
    if fix_missing:
        new_gdf = fix_missing_sjoins(
            target_gdf=new_gdf,
            join_gdf=join_gdf,
            reference_field=reference_field,
            reference_value=reference_value,
            test_join_field=new_column,
            real_join_field=transfer_field,
        )
    return new_gdf

def fix_missing_sjoins(
    target_gdf: gpd.GeoDataFrame,
    join_gdf: gpd.GeoDataFrame,
    reference_field: str = "par_city",  # Field that indicates Cleveland status
    reference_value: str = "CLEVELAND",  # Format to match value if attributed to Cleveland
    test_join_field: str = None,  # Field we are validating
    real_join_field: str = None,  # The source field name to grab
):
    """Fix spatial joins that should not be null by running sjoin_nearest
    on records that should logically not be empty. Typical use case is making sure all shapes within Cleveland
    are successfully joining to geographies that are required for Cleveland property, like ward or neighborhood

    Args:
        gdf: GeoDataFrame = Left geodataframe (usually parcels)
        join_gdf: GeoDataFrame = Right geodataframe (usually reference geography)
        reference_field: str =  Defaults to "par_city" assuming parcels
        reference_value: str = "CLEVELAND", # Format to match value if attributed to Cleveland
        test_join_field: str = "Neighborhood", Field we are validating
        real_join_field:str="SPANM"#Thesourcefieldnametograb.

    Raises:
        ValueError: If a test field isn't indicated

    Returns:
        GeoDataFrame
    """
    if not test_join_field:
        raise ValueError(
            "You must enter the field you want to test for null, i.e. not being found in something that should be in Cleveland."
        )
    # Rows that should be in Cleveland but are testing for bad value
    require_fixes = (target_gdf[reference_field] == reference_value) & (
        target_gdf[test_join_field].isna()
    )
    # Use nearest spatial join to grab these edge cases
    fix_array = gpd.sjoin_nearest(target_gdf[require_fixes], join_gdf)[real_join_field]
    target_gdf.loc[require_fixes, test_join_field] = fix_array
    return target_gdf


def build_aggregator(df,exclude=None,default='sum'):
     """This function prepares a dictionary that defines a aggregation strategy for every column of a dataframe. 
     Such that when groupby() is applied, the dataframe columns are aggregated in accordance to this aggregator dictionary.
     The function automatically searches for numeric columns, and ignores non-numeric columns.
     This function also searches for columns that may be Margins of Error, and applies an appropriate error propogation function to those columns.

     Args:
         df (DataFrame): A pandas DataFrame containing the columns to be aggregated.
         exclude (list or str, optional): A list of columns that will not be aggregated. Defaults to None.
         default (str, optional): The default aggregation strategy. Defaults to 'sum'.

     Returns:
         dictionary: A dictionary of dataframe columns to the aggregation function used in a 'groupby'.
     """
     #Find numeric fields, amd remove fields that are not percentages
     numericTypes = [np.float64,np.int32]
     
     if exclude != None:
        df = df.drop(exclude,axis=1)
        
     df = df.select_dtypes(numericTypes)
     aggregator = {}

     for name in df.columns:
        #If the field is a margin of error, set the aggregator to calculate the margin of error
        if name[-2:] == '_M':
            aggregator[name] = lambda x: calc_moe(x,default)

        #Otherwise set the default aggregator function
        else:
             aggregator[name] = default
     return aggregator

def apportion(left,right,group_key,target_key,aggregator):
    """Aggregates data from one geometry to a different geometry using largest_overlap.

    Args:
        left (GeoDataFrame): The data to be apportioned.
        right (GeoDataFrame): The geometry to which the data from `left` will be apportioned to.
        group_key (str): The ID field of the `right` dataframe.
        target_key (str): The ID field of the `left` dataframe.
        aggregator (str): A dictionary of aggregation rules for each column in the `left` dataframe. This can be built with `build_aggregator`

    Returns:
        GeoDataFrame: An apportioned GeoDataFrame, containing all fields from `right`, and aggregated fields from `left`.
    """

    join = largest_overlap(target_gdf=left,target_key=target_key,join_gdf=right,transfer_field=group_key,new_name=group_key)
    grouped = join.groupby(group_key).agg(aggregator).round(2)
    final = gpd.GeoDataFrame(grouped.merge(right,how='left',left_index=True, right_on=group_key),geometry='geometry',crs=right.crs)
    return final