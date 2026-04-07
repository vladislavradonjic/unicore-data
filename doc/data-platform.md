# Data Platform 

Data platform loosely follows the data mesh paradigm.

Data is organized into data products. There are two basic types of data products:

- source data products that collect data from applications, or other data sources
- consumer data product that collect data from source data products and organize it into forms that are more adapted for data consumption

Data products consist of:

- a relevance matrix
- data
- output ports
- data contract
- data quality controls
- code necessary to generate and refresh data and output ports and enforce designed behaviour

## Relevance matrix

Relavance matrix is barebones specification for the data product. It specifies:

- data product owner (a person)
- data product name,
- for each field, specifically:
	- technical name (name internally used in the data product)
	- business name (human friendly name presented to users)
	- business description (human friendly description of each field and its purpose)
	- lineage (path to source and any transformation applied)
## Data

Data products keep data with bi-temporal historization: each record has a business timestamp and a technical timestamp. Business timestamp is the date and time that the record is referring to. Technical timestamp is the date and time when the record is inserted into a data product.

Records are only ever inserted into data products, never updated or deleted. When refreshing data products, we detect records with changes and new records and insert only those. When a record is deleted in the source, the data product will insert a new row with a deleted_flag with value true.

Data products are typically refreshed once a day and hold up to the previous business day.
## Output ports

Data product data is never used directly. Rather, all users (both technical and human) access data through data product output ports. Output ports are data sets that are refreshed whenever the data product is refreshed, that exposed specific versions of data. 

Typically, there are at least two output ports per data products:

- t-1: data that was valid as of the previous business day
- m-1: data that was valid as of the previous end of month

## Data contract

Is a more verbose data product specification (compared to relevance matrix).

I contains details such as domain and subdomain (business domain and subdomain the the data product belongs to, for example: Risk -> Credit Risk).

In addition to the relevance matrix, it also contains information on how often data product is refreshed, by what time, and output port definitions.

It is important that data contract also contains business descriptions for the data product and output ports.

It also defines which data quality controls are checked whenever the data product and output ports are refreshed and acceptable level of data quality.

## Data quality controls

Each data product should have data quality controls that verify a level data quality that is guaranteed by the data product, as specified in the data product.

## Code

Self explanatory for now.

