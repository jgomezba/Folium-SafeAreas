import folium
from geopy.distance import geodesic
import os

def get_all_list_cominations(lst:list)->list:
    """Function to get all combinations 
    (in pairs) from a list given.

    Args:
        lst (list): original list

    Returns:
        list: list of lists with possible cominations
    """
    pairs = []
    for i in range(len(lst)):
        for j in range(len(lst)):
            if i != j: 
                pairs.append([lst[i],lst[j]])
    return pairs

def plot_homes_security(map:folium.Map, home_locs:list, robbery_cent:list, dang_radius:int,
        safe_col, dang_col)->folium.Map:
    """This function plots homes in map depending if
    they are in a safe or dangerous zone

    Args:
        map (folium.Map): map to draw
        home_locs (list): locations of homes
        robbery_cent (list): center of robberies
        dang_radius (int): distance of danger
        safe_col (_type_): color of safe zone
        dang_col (_type_): color of danger zone

    Returns:
        folium.Map: map with homes included
    """
    
    if safe_col == None:
        safe_col = "green"
    if dang_col == None:
        dang_col = "red"
    
    for new_marker_location in home_locs:
        distance = geodesic(new_marker_location, robbery_cent).meters
        
        if distance <= dang_radius:
            folium.Marker(location=new_marker_location, icon=folium.Icon(color=dang_col, icon='home')).add_to(map)
        else:
            folium.Marker(location=new_marker_location, icon=folium.Icon(color=safe_col, icon='home')).add_to(map)
    
    return map

def plot_danger_zone(map:folium.Map, robbery_loc:list, robbery_cent:list,danger_col,
        border_radius_col, fill_radius_col, dang_radius:int) -> folium.Map:
    """This functions plots in a folium map danger zones with
    an specified icon and calculates a radius of danger and every 
    arist of every robbery location to measure thief trayectory.

    Args:
        map (folium.Map): map to draw
        robbery_loc (list): contains robbery locations
        robbery_cent (list): contains center of robbery locations
        danger_col (_type_): danger color
        border_radius_col (_type_): border color of danger circle 
        fill_radius_col (_type_): fill color of danger circle
        dang_radius (int): danger distance

    Returns:
        folium.Map: map with danger circle zone and lines added
    """
    
    if danger_col == None:
        danger_col = 'red'
        
    folium.Marker(location=robbery_cent, icon=folium.Icon(color=danger_col, icon='point')).add_to(map)
    
    if border_radius_col == None:
        border_radius_col = 'crimson'
    if fill_radius_col == None:
        fill_radius_col = 'crimson'
    
    folium.Circle(
            location=robbery_cent,
            radius= dang_radius,
            color= border_radius_col,
            fill=True,
            fill_color=fill_radius_col
        ).add_to(map)

    #Create lines joining markers, but add first item again
    folium.PolyLine(locations=get_all_list_cominations(robbery_loc), color=danger_col, weight=2, opacity=0.7,).add_to(map)
    
    return map


def plot_robbery_markers(map:folium.Map, robbery_locs:list, street_locs):
    """This functions plots in a folium map robbery zones with
    markers associated

    Args:
        map (folium.Map): map to draw
        robbery_locs (list): robbery locations
        street_locs (_type_): street names of locations

    Returns:
        folium.Map: map with danger zones added
    """
    i=0
    for location in robbery_locs:
        icon_robbery = folium.features.CustomIcon('./images/thief_3.png', icon_size=(50,50))
        if street_locs != None:
            try:
                folium.Marker(location=location,popup=street_locs[i],icon=icon_robbery).add_to(map)
            except:
                print("Please, revise if locations are correct and street_names list have the same len")
        else:
            folium.Marker(location=location,icon=icon_robbery).add_to(map)
        i+=1

    return map


def plot_safe_home_from_robbery(robbery_locations:list, home_locations:list, danger_radius:int, 
        map_zoom:float = 14, border_radius_color:str = None, fill_radius_color:str = None, 
        street_names:list = None, safe_color:str = None, danger_color:str = None):

    #calculate mean point of robbery markers
    mean_lat = sum([pos[0] for pos in robbery_locations]) / len(robbery_locations)
    mean_lon = sum([pos[1] for pos in robbery_locations]) / len(robbery_locations)
    
    robbery_center = [mean_lat, mean_lon]
    
    #create map object intialized in mean location of robberies
    m = folium.Map(location=robbery_center, zoom_start=map_zoom)
    
    #plot robbery markers
    m = plot_robbery_markers(m, robbery_locations, street_names)
    
    #plot center of robbery marker and circle radius with lines
    m = plot_danger_zone(m,robbery_locations, robbery_center, danger_color, border_radius_color,
        fill_radius_color, danger_radius)

    #Evaluate new markers
    m = plot_homes_security(m, home_locations, robbery_center, danger_radius, safe_color,danger_color)
    
    #generate map and save as local file
    script_directory = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_directory, "index.html")
    m.save(file_path)
    print(f"Map generated in {file_path}")
    
if __name__ == "__main__":

    #Alcorcon last robbery locations
    robbery_locations = [[40.350700, -3.819300],
                        [40.3493175, -3.8061377],
                        [40.3452728, -3.8247379],
                        [40.3386008, -3.8107881],
                        [40.352045,-3.8147584]]
    street_names = ['Plaza Príncipes', 
                    'Avenida Viñagrande', 
                    'Calle la Nacho',
                    'Calle los pintores',
                    'Calle Cabo San Vicente']
    
    #Evalate homes in same city
    home_locations = [[40.3342442, -3.8240913], 
                    [40.3542, -3.8084], 
                    [40.3492635, -3.8242727],
                    [40.3471204,-3.8340317],
                    [40.35098695,-3.8051485610200046]]

    #plot to html
    plot_safe_home_from_robbery(robbery_locations, home_locations,
            danger_radius= 950, street_names=street_names)
