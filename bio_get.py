import requests

def nps_unit_list() -> list:
    '''
    Returns a list of National Park Service (NPS) unit codes.
    '''
    unit_list_url = 'https://services1.arcgis.com/fBc8EJBxQRMcHlei/arcgis/rest/services/NPS_Land_Resources_Division_Boundary_and_Tract_Data_Service/FeatureServer/0/query?where=1%3D1&outFields=UNIT_CODE&f=json'
    request = requests.get(unit_list_url, timeout=20)
    unit_list_data = request.json()
    park_units = []
    
    for item in unit_list_data['features']:
        park_units.append(item['attributes']['UNIT_CODE'])
    
    return park_units

def npsspp_v3_api(park_units: list|str = None, categories: list|str = None, list_type: str = 'checklist', print_progress: bool = False) -> list:
    '''
    Returns records in the NPSpecies (v3) database for specified park units. If no units are provided, all data is retrieved.

    Params:
    `park_units`: List of NPS unit codes. A string can also be used for a single unit.
    `Categories`: List of species categories to filter on. A string can also be used for a single category.
        Accepted Values: `'Vascular Plant'`, `'Reptile'`, `'Amphibian'`, `'Fish'`, `'Mammal'`, `'Bird'`
        Default: `None`
        Note: Due to how the NPSpecies API functions, these values can be passed as upper/lower case and the values 1-5 can also be used and correlate to a specific category.
    `list_type`: Type of data to return.
        Accepted Values: `'checklist'`,`'detaillist'`,`'fulllist'`
        Default: `'checklist'`
    `print_progress`: Whether to print the position in `park_units`, name of park units, and number of records. Useful for seeing the time remaining when getting data for many units.
        Default: `True`
    '''
    base_url = 'https://irmaservices.nps.gov/NPSpecies/v3/rest/'
    base_url = base_url + list_type + '/'
    park_data = []
    count = 1

    #Get Park Unit List/Format
    if park_units is None:
        park_units = nps_unit_list()
    elif isinstance(park_units, str):
        park_units = [park_units]

    #Format Categories
    if categories is not None:
        if isinstance(categories, list):
            categories = categories.join(',')
        categories = categories.replace(' ','%20')
        categories = '/' + categories
    else:
        categories = ''

    #API Request
    for unit in park_units:
        unit_url = base_url + unit + categories + '?&format=Json'
        request = requests.get(unit_url, timeout=45)
        if request.status_code == 200:
            unit_data = request.json()
            park_data = park_data + unit_data
            record_count = f', {len(unit_data)} Records'
        else:
            record_count = ', No API Response'
        if print_progress is True:
            print(f'{count}/{len(park_units)}: {unit}{record_count}')
            count += 1
    return park_data
