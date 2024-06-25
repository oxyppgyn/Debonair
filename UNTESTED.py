"""
ARCGIS
"""
import arcpy

def reset_stats_fields(table, field_list: list = None, rep_alias: bool = True) -> None:
    '''
    Resets statistics field names after using tools like dissolve.
    `table`: Table to be updated.
    `field_list`: List of fields to be updated. Default: None, all fields updated.
    `rep_alias`: If the field alias will be updated. Default: True.
    '''
    field_prefixes = ['SUM_','MEAN_','MIN_','MAX_','RANGE_','STD_','COUNT_','FIRST_',
                      'LAST_','MEDIAN_','VARIANCE_','UNIQUE_','CONCATENATE_']
    if field_list is None:
        field_list = [field.name for field in arcpy.ListFields(table)]
    for field in field_list:
        if any(item in field for item in field_prefixes):
            rem_val = [item for item in field_prefixes if item in field]
            field_rep = field.replace(rem_val[0],'')
            if rep_alias is True:
                arcpy.management.AlterField(in_table = table, field = field, new_field_name = field_rep, new_field_alias = field_rep)
            else:
                arcpy.management.AlterField(in_table = table, field = field, new_field_name = field_rep)

def selection_count(table) -> int:
    '''
    Returns a count of the number of records selected in a table.
    Returns -1 if all records in a table are selected.
    `Table`: Table with records to be counted.
    '''
    if arcpy.Describe(table).FIDSet:
        records = arcpy.GetCount_management(table)
        count = int(records.getOutput(0))
        if count == int(arcpy.management.GetCount(table)[0]):
            return -1
        else:
            return count
    else:
        return 0

def update_records_from(from_table, to_table, fields: list|dict, method: str):
    '''
    Updates attributes from one table using values from another.
    `from_table`: Table that attributes will be pulled from.
    `to_table`: Table that will have its records updated.
    `fields`: Fields that will be updated/used to update records. If a list is used, the fields will be used in both tables. If a dictionary is used, fields will be mapped as key, value pairs. If only one field is used, it may be input as a list or string.
    `Method`: Method used to update records.
        `1:1`: One-to-one, matches each record in the input table to a record in the output table. The order of records in each table is used to determine match order.
        `1:m`: One-to-many, matches one selected record from the in table to multiple in the out table.
    '''
    #Assign fields to list variables
    if fields is any([],{},'*'):
        from_list = '*'
        to_list = '*'
    elif isinstance(fields, list):
        from_list = fields
        to_list = fields
    elif isinstance(fields, dict):
        from_list = list(fields.keys())
        to_list = list(fields.values())
    else:
        from_list = [fields]
        to_list = [fields]

    #Methods
    if method == '1:1':
        if selection_count(from_table) != selection_count(to_table):
            raise Exception('Number of records selected in input table is not equal to number selected in output table, but 1:1 relationship specified.')
        raise NotImplementedError()

    elif method == '1:m':
        if selection_count(from_table) > 1:
            raise Exception('More than 1 record selected in input table, but 1:m relationship specified.')
        with arcpy.da.SearchCursor(from_table, from_list) as search_cursor:
            row_from = next(search_cursor)
            value_from = row_from[0]
        with arcpy.da.UpdateCursor(to_table, to_list) as update_cursor:
            for row_to in update_cursor:
                # Set the value in Table B to the value from Table A
                row_to[0] = value_from
                update_cursor.updateRow(row_to)
    else:
        raise ValueError(f'{method} is not a valid value for "method". Valid values are: "1:1" and "1:m".')