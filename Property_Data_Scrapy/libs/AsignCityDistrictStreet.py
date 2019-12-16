import urllib
import json
import urllib.request
from urllib.request import quote, unquote 

def AsignCity(lon,lat):
	url1 = "http://restapi.amap.com/v3/geocode/regeo?s=rsv3&key=676f71aeb9e8fa578086d3964399ed4e&location="
	url2 = str(lon)+","+str(lat)
	url3 = "http://10.1.10.230:6080/arcgis/rest/services/SL/XZJX1/FeatureServer/2/query?where=1%3D1&objectIds=&time=&geometry="
	url4 = "&geometryType=esriGeometryPoint&inSR=4326&spatialRel=esriSpatialRelIntersects&relationParam=&outFields=*&returnGeometry=false&maxAllowableOffset=&geometryPrecision=&outSR=&gdbVersion=&returnDistinctValues=false&returnIdsOnly=false&returnCountOnly=false&orderByFields=&groupByFieldsForStatistics=&outStatistics=&returnZ=false&returnM=false&f=pjson"
	#url = url1 + url2
	url = url3+url2+url4
	#urldata=quote(url,safe=";/?:@&=+$,", encoding="utf-8")
	urldata = url
	user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
	req = urllib.request.Request(urldata, headers={'User-Agent': 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'})
	html = urllib.request.urlopen(req)
	hjson=json.loads(html.read())
	city = str(hjson['features'][0]['attributes']['CSMC'])
	return (city)

def AsignDistrict(lon,lat):
	url1 = "http://restapi.amap.com/v3/geocode/regeo?s=rsv3&key=676f71aeb9e8fa578086d3964399ed4e&location="
	url2 = str(lon)+","+str(lat)
	url3 = "http://10.1.10.230:6080/arcgis/rest/services/SL/XZJX1/MapServer/2/query?where=1%3D1&objectIds=&time=&geometry="
	url4 = "&geometryType=esriGeometryPoint&inSR=4326&spatialRel=esriSpatialRelIntersects&relationParam=&outFields=*&returnGeometry=false&maxAllowableOffset=&geometryPrecision=&outSR=&gdbVersion=&returnDistinctValues=false&returnIdsOnly=false&returnCountOnly=false&orderByFields=&groupByFieldsForStatistics=&outStatistics=&returnZ=false&returnM=false&f=pjson"
	url = url3+url2+url4
	urldata = url
	user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
	req = urllib.request.Request(urldata, headers={'User-Agent': 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'})
	html = urllib.request.urlopen(req)
	hjson=json.loads(html.read())
	district = str(hjson['features'][0]['attributes']['FQMC'])
	return (district)

def AsignStreet(lon,lat):
	url1 = "http://restapi.amap.com/v3/geocode/regeo?s=rsv3&key=676f71aeb9e8fa578086d3964399ed4e&location="
	url2 = str(lon)+","+str(lat)
	url3 = "http://10.1.10.230:6080/arcgis/rest/services/SL/XZJX1/MapServer/2/query?where=1%3D1&objectIds=&time=&geometry="
	url4 = "&geometryType=esriGeometryPoint&inSR=4326&spatialRel=esriSpatialRelIntersects&relationParam=&outFields=*&returnGeometry=false&maxAllowableOffset=&geometryPrecision=&outSR=&gdbVersion=&returnDistinctValues=false&returnIdsOnly=false&returnCountOnly=false&orderByFields=&groupByFieldsForStatistics=&outStatistics=&returnZ=false&returnM=false&f=pjson"
	url = url3+url2+url4
	urldata = url
	user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
	req = urllib.request.Request(urldata, headers={'User-Agent': 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'})
	html = urllib.request.urlopen(req)
	hjson=json.loads(html.read())
	street = str(hjson['features'][0]['attributes']['ZJMC'])
	return (street)
