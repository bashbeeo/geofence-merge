import csv
import string
import pandas as pd
import geopandas as gpd
from shapely import Polygon, to_geojson
import numpy as np
import matplotlib.pyplot as plt
import json
geofencesList = list()
groupedData = {}
# opening the CSV file
with open('geofences.csv', mode ='r',encoding='utf-8-sig') as file:
# reading the CSV file
  reader = csv.reader(file)
  for n, row in enumerate(reader):
    if not n:
      # Skip header row (n = 0).
      continue  
    integrationId, geofence = row
    if integrationId not in groupedData:
      groupedData[integrationId] = list()
    groupedData[integrationId].append(geofence)
  csvData = []
  for integrationId, geofencesList in groupedData.items():
    #if integrationId == 'Gireeb1355':
      data = dict()
      for lineIndex,line in enumerate(geofencesList):
        s = line.replace(' ','')
        s = s.replace('),','|')
        s = s.replace(')','')
        s = s.replace('(','')
        arr = s.split('|')
        #print(arr)
        for points in arr:
          splittedPoints = points.split(',')
          #print(splittedPoints)
          splittedPoints = map(lambda s: float(s),splittedPoints)
          splittedPoints = list(splittedPoints)
          tupleOfPoints = (splittedPoints[1],splittedPoints[0])
          if lineIndex in data.keys():
            data[lineIndex].append(tupleOfPoints)
          else:
            data[lineIndex] = list()
            data[lineIndex].append(tupleOfPoints)
      dfData = {
        "line number":[],
        "wkt":[],
      }
      for key,points in data.items():
        dfData['line number'].append("Line "+str(key))
        p = Polygon(points)
        if p.is_valid == False:
          p = p.buffer(0)
        dfData['wkt'].append(p.wkt)
      df = pd.DataFrame(dfData)
      gs = gpd.GeoSeries.from_wkt(df['wkt'])
      gdf = gpd.GeoDataFrame(df, geometry=gs)
      #f, axes = plt.subplots(figsize=(20, 10), ncols=2, nrows=1)  
      #gdf.plot(ax=axes[0],cmap='OrRd', alpha=0.3)
      unionPolygon = gpd.GeoSeries(gdf['geometry']).unary_union
      #final = gpd.GeoDataFrame({"name":["final"],"geometry":[unionPolygon]})
      geoJson = json.loads(to_geojson(unionPolygon))
      #numpy_array = np.array(geoJson['coordinates'])
      coords = geoJson['coordinates']
      #print(coords[0])
      #print(len(coords[0]))
      if geoJson['type'] == 'MultiPolygon':
        for polygons in coords:
          geopointsStr = ''
          #for polygon in polygons:
          for points in polygons[0]:
            geopointsStr += '('+str(points[1])+','+str(points[0])+'),'
          geopointsStr = geopointsStr[:len(geopointsStr)-1] # Remove last character as it will be a comma
          csvData.append([integrationId,geopointsStr])
      if geoJson['type'] == 'Polygon':
        #print(coords[0][0])
        #print(len(coords[0][0]))
        geopointsStr = ''
        #for polygon in coords:
        for points in coords[0]:
          geopointsStr += '('+str(points[1])+','+str(points[0])+'),'
        geopointsStr = geopointsStr[:len(geopointsStr)-1] # Remove last character as it will be a comma
        csvData.append([integrationId,geopointsStr])
      #final.plot(ax=axes[1])
      #plt.savefig(integrationId+'.png')
with open('output.csv', mode ='w',encoding='utf-8-sig') as file:
  writer = csv.writer(file)
  writer.writerow(['integration_id','geofence'])
  writer.writerows(csvData)

