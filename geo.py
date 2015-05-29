import matplotlib.path as mplPath
import numpy as np
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
    for index in indices:
        try:
            fips = county_geo_dictionary((county_geo[index][0],county_geo[index][1]))
            fips_list.append(fips)
        except:
            pass
    if len(fips_list) > 0:
        for fips_num in fips_list:
            county_paths = all_county_boundaries[string(fips_num)]
            if find_nested(county_paths) == 0:
                if in_polygon(point, county_paths):
                    return fips_num
                    break
            else:
                for path in county_paths:
                    if in_polygon(point, county_paths):
                        return fips_num
                        break
    return None

locations = [["bronx", [[40.915132, -73.912168],[40.799059, -73.918005],[40.814391, -73.779302],[40.881655, -73.782735]]], ["harlem", [[40.834370, -73.950320],[40.818913, -73.961478],[40.801243, -73.959247],[40.797084, -73.949290],[40.817614, -73.934012],[40.828006, -73.934871]]], ["upper_west", [[40.818913, -73.961478],[40.801243, -73.959247],[40.768767, -73.982015],[40.773057, -73.993516]]], ["upper_east", [[40.797084, -73.949290],[40.817614, -73.934012],[40.764275, -73.972852],[40.758798, -73.958775],[40.776219, -73.941094],[40.799159, -73.928306],]], ["midtown", [[40.801243, -73.959247],[40.768767, -73.982015],[40.764275, -73.972852],[40.758798, -73.958775],[40.726881, -73.971736],[40.745416, -74.015509]]], ["downtown", [[40.726881, -73.971736],[40.745416, -74.015509],[40.697279, -74.021947],[40.711984, -73.971307]]], ["brooklyn", [[40.738697, -73.965254],[40.707995, -73.972120],[40.704351, -73.996839],[40.674674, -74.029112],[40.607982, -74.049024],[40.559485, -74.020185],[40.601727, -73.820371],[40.694981, -73.869810]]], ["queens", [[40.694981, -73.869810],[40.738697, -73.965254],[40.791007, -73.908958],[40.801923, -73.775748],[40.731196, -73.705710],[40.574394, -73.754462],[0.544137, -73.952216],[40.566049, -73.915824],[40.601727, -73.820371]]], ["san_fran", [[37.707196, -122.503175],[37.711270, -122.348679],[37.837188, -122.364366],[37.800303, -122.527787]]], ["west_bay", [[37.416526, -121.994411],[37.361970, -122.120067],[37.627261, -122.498996],[37.707196, -122.503175],[37.711270, -122.348679]]], ["east_bay", [[37.486844, -121.872875],[37.451966, -121.947033],[37.502835, -122.102708],[37.961171, -122.443285],[38.080176, -122.165880]]], ["south_bay", [[37.486844, -121.872875],[37.451966, -121.947033],[37.416526, -121.994411],[37.361970, -122.120067],[37.222672, -121.927807],[37.305189, -121.750652]]]]

def find_location(point):
  for area in locations:
    if in_polygon(point,area[1]):
      return area[0]
      break
  else:
    return None
