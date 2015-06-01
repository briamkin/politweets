from __future__ import division
from geo_boundaries import all_county_boundaries
from county_geo import county_geo, county_geo_dictionary, county_fips
from sklearn.externals import joblib

def in_polygon(point, poly):
    """Return True of point is in polygon path"""
    x = point[0]
    y = point[1]
    n = len(poly)
    status = False
    p1x,p1y = poly[0]
    for i in range(n+1):
        p2x,p2y = poly[i % n]
        if min(p1y,p2y) < y <= max(p1y,p2y):
            if x <= max(p1x,p2x):
                if p1y != p2y:
                    xinters = (y-p1y)*(p2x-p1x)/(p2y-p1y)+p1x
                if p1x == p2x or x <= xinters:
                    status = not status
        p1x,p1y = p2x,p2y

    return status

def geo_dist(p1,p2):
    """Return distance between 2 ong/lat points"""
    return sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)

def find_nested(nested_list):
    """Return 1 for nested geo coordinates and 0 if not nested"""
    try:
        nested_list[0][0][0]
        nest = 1
    except:
        nest = 0
    return nest

def find_county(point, full=0):
    """Given a long/lat point in the United States return a
    corresponding FIPS ID"""

    # load, run KD Tree, and return 5 nearest points
    county_tree = joblib.load('geo_tree/county_tree.pkl')
    dist, indices = county_tree.query(point, k=5)
    fips_list = []
    for index in indices[0]:

        # print county_geo[index][0],county_geo[index][1]
        try:
            fips = county_geo_dictionary[(county_geo[index][0],county_geo[index][1])]
            fips_list.append(fips)
        except:
            pass

    # set default values for return
    fips = fips_list[0]

    # Find which path it exists in
    if len(fips_list) > 0:
        for fips_num in fips_list:
            county_paths = all_county_boundaries[str(fips_num)]
            if find_nested(county_paths) == 0:
                if in_polygon(point, county_paths):
                    fips = fips_num
                    break
            else:
                for path in county_paths:
                    if in_polygon(point, path):
                        fips = fips_num
                        break

    # Point is most likely outside of US, return None
    if dist[0][0] > 6:
        return None

    # If point is near but not in county, return nearest county
    if full == 1:
        try:
            return [fips,county_fips[int(fips)][1],county_fips[int(fips)][0]]
        except:
            return None
    else:
        return fips
