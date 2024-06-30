import warnings

PORTAL_ITEM_TYPES = ['360 VR Experience','CityEngine Web Scene','Map Area','Pro Map','Web Map','Web Scene','Feature Collection','Feature Collection Template','Feature Service','Geodata Service','Group Layer','Image Service','KML','KML Collection','Map Service','OGCFeatureServer','Oriented Imagery Catalog','Relational Database Connection','3DTilesService','Scene Service','Vector Tile Service','WFS','WMS','WMTS','Geometry Service','Geocoding Service','Geoprocessing Service','Network Analysis Service','Workflow Manager Service','AppBuilder Extension','AppBuilder Widget Package','Code Attachment','Dashboard','Data Pipeline','Deep Learning Studio Project','Esri Classification Schema','Excalibur Imagery Project','Experience Builder Widget','Experience Builder Widget Package','Form','GeoBIM Application','GeoBIM Project','Hub Event','Hub Initiative','Hub Initiative Template','Hub Page','Hub Project','Hub Site Application','Insights Workbook','Insights Workbook Package','Insights Model','Insights Page','Insights Theme','Insights Data Engineering Workbook','Insights Data Engineering Model','Investigation','Knowledge Studio Project','Mission','Mobile Application','Notebook','Notebook Code Snippet Library','Native Application','Native Application Installer','Ortho Mapping Project','Ortho Mapping Template','Solution','StoryMap','Web AppBuilder Widget','Web Experience','Web Experience Template','Web Mapping Application','Workforce Project','Administrative Report','Apache Parquet','CAD Drawing','Color Set','Content Category Set','CSV','Document Link','Earth configuration','Esri Classifier Definition','Export Package','File Geodatabase','GeoJson','GeoPackage','GML','Image','iWork Keynote','iWork Numbers','iWork Pages','Microsoft Excel','Microsoft Powerpoint','Microsoft Word','PDF','Report Template','Service Definition','Shapefile','SQLite Geodatabase','Statistical Data Collection','StoryMap Theme','Style','Symbol Set','Visio Document','ArcPad Package','Compact Tile Package','Explorer Map','Globe Document','Layout','Map Document','Map Package','Map Template','Mobile Basemap Package','Mobile Map Package','Mobile Scene Package','Project Package','Project Template','Published Map','Scene Document','Task File','Tile Package','Vector Tile Package','Explorer Layer','Image Collection','Layer','Layer Package','Pro Report','Scene Package','3DTilesPackage','Desktop Style','ArcGIS Pro Configuration','Deep Learning Package','Geoprocessing Package','Geoprocessing Package (Pro version)','Geoprocessing Sample','Locator Package','Raster function template','Rule Package','Pro Report Template','ArcGIS Pro Add In','Code Sample','Desktop Add In','Desktop Application','Desktop Application Template','Explorer Add In','Survey123 Add In','Workflow Manager Package']

def portal_query_type(gis, filter_type: str = '' ,type_filter: list = []):
    #Check filter against item type list
    if filter_type == 'Exclude':
        type_filter[:] = [i for i in PORTAL_ITEM_TYPES if i not in type_filter]
    elif filter_type == 'Include':
        type_filter[:] = [i for i in PORTAL_ITEM_TYPES if i in type_filter]
    elif filter_type == '' or type_filter == []:
        pass
    else:
        raise Exception(f'Correct filter type not specified. Exclude, Include, or an empty string are the only accepted inputs. Your input: {filter_type}.')
    
    #Try regular search
    ##If over 500, search by user
    ##If user has over 500, try to search by item type and user
    if type_filter != []:
        query = '" OR "'.join(type_filter)
        query = f'type: ("{query}")'
        items = gis.content.search(query=f'{query}, NOT owner: esri*', max_items=500)
    else:
        items = gis.content.search(query='NOT owner:esri*', max_items=500) 

    if len(items) == 500:
        items.clear()
        users = gis.users.search(max_users = 10000)
        users = [user for user in users if user.storageUsage != 0]
        for user in users:
            if type_filter != []:
                items_by_user = gis.content.search(query=f'{query}, owner: {user.username}', outside_org=False, max_items=500)
            else:
                items_by_user = gis.content.search(query=f'owner: {user.username}', outside_org=False, max_items=500)
            
            if not items_by_user:
                pass
            elif len(items_by_user) < 500:
                items.extend(items_by_user)
            elif len(items_by_user) != 500:
                for item_type in type_filter:
                    items_by_type = gis.content.search(query=f'type: {item_type} AND owner: {user.username}',  outside_org=False, max_items=500)
                    if len(items_by_type) == 0:
                        pass
                    if len(items_by_type) == 500:                
                        warnings.warn(f'{user.username} has over 500 portal items of a single type. Unable to query all {item_type} items. Items currently queried added to content list.')
                        items.extend(items_by_type)
                    else:
                        items.extend(items_by_type)
            else:
                Exception('More than 500 items returned. Please update script with new max_items arguement.')
    elif len(items) == 0:
        raise Exception('No items returned with the function gis.content.search.')
    return items

def portal_tag_list(items) -> dict:
    tag_list = []
    for item in items:
        for tag in item.tags:
            tag_list.append(tag)
    tag_dict = {'Tag Name':[],'Count':[]}
    tag_values = set(tag_list)
    for value in tag_values:
        count = len([tag for tag in tag_list if tag == value])
        tag_dict['Count'].append(count)
        if value == '':
            value = '<No Tags>'
        tag_dict['Tag Name'].append(value)
    return tag_dict

def portal_tag_update(items, tag_mapping, update: bool = False, gis = 'N/A'):
    tag_dict = {'Item ID':[], 'Old Tags':[],'New Tags':[]}
    for item in items:
        new_tags = [tag_mapping.get(i,i) for i in item.tags]
        if len(item.tags) > 0 and item.tags != ['']:
            new_tags = list({tag for tag in new_tags if tag != ''})
            if new_tags != list(set(item.tags)) and item.tags != []:
                tag_dict['New Tags'].append(new_tags)
            else:
                tag_dict['New Tags'].append(None)
        else:
            tag_dict['New Tags'].append(None)
        tag_dict['Item ID'].append(item.id)
        tag_dict['Old Tags'].append(item.tags)
    if update is True and gis != 'N/A':
        for index in range(len(tag_dict['Item ID'])):
            if tag_dict['New Tags'][index] is None:
                update_item = gis.content.get(tag_dict['Item ID'][index])
                update_item.update(item_properties={'tags':tag_dict['New Tags'][index]})
    elif update is True and gis == 'N/A':
        warnings.warn('Update set to true, but GIS login object not provided.')
    return tag_dict