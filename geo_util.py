import arcpy

def zoom_to_selection(selection_layer, scale = None, reset_selection = False):
    '''
    Zooms to the extent of a selected feature. If no features are selected, zooms to the center of the feature.
    `selection_feature`: Map layer with the extent used for zoom in/out.
    `scale`: Map scale to zoom to. Can be an interger or string representing a scale ratio (int:int).
        Default: `None`
    reset_selection: If the current selection should be reset after zooming.
        Default: `False`
    '''
    #Pan to Extent
    current_map = arcpy.mp.ArcGISProject("CURRENT").activeMap
    map_view = arcpy.mp.ArcGISProject("CURRENT").activeView
    map_layer = current_map.listLayers(selection_layer)[0]
    extent = map_view.getLayerExtent(map_layer, True, True)
    map_view.panToExtent(extent)
    
    #Change Scale
    if scale is not None:
        if isinstance(scale,str):
            if ':' in scale:
                scale = scale.split(':')
                scale = int(scale[1])/int(scale[0])
        map_view.camera.scale = scale
    
    #Reset Selection
    if reset_selection is True:
        arcpy.management.SelectLayerByAttribute(in_layer_or_view = selection_layer, selection_type = "CLEAR_SELECTION", where_clause = "", invert_where_clause = None)
    
    return extent