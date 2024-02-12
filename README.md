# cledatatoolkit
Library of tools published by City of Cleveland's Office of Urban Analytics, meant for for civic data analysis using local, county and regional data sources, including datasets Cleveland's new Open Data Portal.

## Installation
You can use `pip` in your terminal to install Urban AI's package.

```
pip install cle-data-toolkit
```
This will also install dependencies such as geopandas, pandas, and Jupyter-notebook support.

We recommending installing into a [virtual environment](https://docs.python.org/3/library/venv.html) to not modify your base version of Python.

## Features

### Spatial Helper Functions
* Apportioning: Allocating Census data to local boundaries that don't align
* Custom functions built on top of `geopandas` for more advanced spatial joins
    * Largest overlap
### County Property Data Enhancement
* Extracting insights from property owner names
* Standardizing property types and ownership

## Guide
See our tutorial notebook repo, [**open-data-examples**](https://github.com/City-of-Cleveland/open-data-examples), for curated tutorials of how you might use this package with Cleveland civic data sources!
