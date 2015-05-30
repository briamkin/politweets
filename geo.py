import matplotlib.path as mplPath
import numpy as np
from geo_boundaries import all_county_boundaries
from county_geo import county_geo, county_geo_dictionary
from sklearn.externals import joblib
import numpy as np

def in_polygon(point, poly):
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

def find_nested(nested_list):
    try:
        nested_list[0][0][0]
        nest = 1
    except:
        nest = 0
    return nest

def find_county(point):
    county_tree = joblib.load('county_tree.pkl')
    dist, indices = county_tree.query(point, k=5)
    fips_list = []
    for index in indices[0]:
        print county_geo[index][0],county_geo[index][1]
        try:
            fips = county_geo_dictionary[(county_geo[index][0],county_geo[index][1])]
            fips_list.append(fips)
        except:
            pass
    if len(fips_list) > 0:
        for fips_num in fips_list:
            county_paths = all_county_boundaries[str(fips_num)]
            if find_nested(county_paths) == 0:
                if in_polygon(point, county_paths):
                    return fips_num
                    break
            else:
                for path in county_paths:
                    if in_polygon(point, path):
                        return fips_num
                        break
    return fips_list[0]
