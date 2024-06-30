def selection_count(table) -> int:
    '''
    Returns a count of the number of records selected in a table. Returns -1 if all records in a table are selected.
    `Table`: Table with records to be counted.
    '''
    if arcpy.Describe(table).FIDSet:
        records = arcpy.GetCount_management(table)
        count = int(records.getOutput(0))
        if count == '''ACTUAL FULL RECORD COUNT''': # <---- Figure out
            return -1
        return count
    else:
        return 0

def transfer_attributes(in_table, out_table, in_fields = list|str, out_fields: list|str = None, reset_selection: bool = True, max_selection: int = 1) -> None:
    '''
    Transfers attributes from a selected record in one table to selected record(s) in another. Acts in a 1-m relationship.
    `in_table`: Input table to copy records from.
    `out_table`: Output table to copy attributes to.
    `in_fields`: List of fields in the input table to copy. A string can also be used for a single field.
    `out_fields`: List of fields in the output table to copy to. If no fields are provided, the list specified in `in_fields` will be used. A string can also be used for a single field.
        Default: `None`
    reset_selection`: If the current selection should be reset after transferring attributes.
        Default: `True`
    `max_out_selection`: Maximum number of records that can be selected in the output table.
        Default: `1`
    '''
    #If no out_field, assign in_field
    if isinstance(in_fields, str):
        in_fields = list(in_fields)
    
    if out_fields is None:
        out_fields = in_fields

    #Check Selection Count and Field Lists
    if selection_count(in_table) != 1:
        raise Exception('More than one record selected in input table.')
    if selection_count(out_table) < 1:
        raise Exception('No output record(s) selected.')
    if selection_count(out_table) > max_selection:
        raise Exception('Number of records selected in out table exceeds max_out_selection.')
    if len(in_fields) != len(out_fields):
        raise Exception(f'Cannot match fields one-to-one, a different number of fields was specified for input and output.\n Input: {len(in_fields)}, Output: {len(in_fields)}.')

    for index in enumerate(in_fields):
        #Get Value from in_table with SearchCursor
        with arcpy.da.SearchCursor(in_table, in_fields[index]) as search_cursor:
            in_row = next(search_cursor)
            in_val = in_row[0]

        ##Update Values in out_table with Update Cursor
        with arcpy.da.UpdateCursor(out_table, out_fields[index]) as update_cursor:
            for out_row in update_cursor:
                out_row[0] = in_val
                update_cursor.updateRow(out_row)
                
    #Reset Selection
    if reset_selection == True:
        arcpy.management.SelectLayerByAttribute(in_layer_or_view = in_table, selection_type = "CLEAR_SELECTION", where_clause = "", invert_where_clause = None)
        arcpy.management.SelectLayerByAttribute(in_layer_or_view = out_table, selection_type = "CLEAR_SELECTION", where_clause = "", invert_where_clause = None)
        
def replace_attributes(table, fields = list|str, replace_value = None, reset_selection: bool = True, max_selection: int = 1) -> None:
    '''
    Replaces (or clears as <Null>) selected records in a table.
    `table`: Input table to copy records from.
    `fields`: List of fields in the table to replace attributes of. A string can also be used for a single field.
    `replace_value`: Value to replace attributes with. By default attributes are set to <Null> (equivalent to Pythonic `None`).
        Default: 'None'
    reset_selection`: If the current selection should be reset after transferring attributes.
        Default: `True`
    `max_selection`: Maximum number of records that can be selected in the table.
        Default: `1` 
    '''
    #Check Selection Count
    if selection_count(table) < 1:
        raise Exception('No output record(s) selected.')
    if selection_count(table) > max_selection:
        raise Exception('Number of records selected in table exceeds max_selection.')
    
    #Update Fields
    if isinstance(fields,str):
        fields = list(fields)
    codeblock = f"""def return_val():
        return {replace_value}"""
    for field in fields:
        arcpy.management.CalculateField(in_table = table, field = field, expression = 'return_val()', code_block = codeblock)
    
    #Reset Selection
    if reset_selection is True:
        arcpy.management.SelectLayerByAttribute(in_layer_or_view = table, selection_type = "CLEAR_SELECTION", where_clause = "", invert_where_clause = None)

def select_first_record(table, id_field: str = 'OBJECTID'):
    '''
    Selects the first record in a table.
    `table`: Input table to select from
    `id_field`: Name of field that will be used to search find and select the first record. This field must have unique values for each record.
        Default: `'OBJECTID'`
    '''
    with arcpy.da.SearchCursor(table, id_field) as search_cursor:
        id_value = next(search_cursor)[0]
        arcpy.management.SelectLayerByAttribute(in_layer_or_view = table,
            selection_type = 'NEW_SELECTION', where_clause = f'{id_field} = {id_value}')
        return id_value
