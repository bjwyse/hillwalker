# Create your views here.
from django.shortcuts import render_to_response
import urllib2
import urllib
import json
import pprint
import matplotlib
import numpy as np
import matplotlib.pyplot as plt

GRID_DIVISIONS = 20
API_KEY = "Fmjtd%7Cluu7n1u2nq%2C2l%3Do5-5rbad"

def home(request):
    return render_to_response('map/home.html')

def contour_image(request):
    ul = request.GET.get('ul')
    lr = request.GET.get('lr')
    print "Parameters"
    print "Upper Left: ", ul
    print "Lower Right: ", lr
    
    upper_lat, left_lng = ul.split(',')
    lower_lat, right_lng = lr.split(',')
    
    print ("lat from %s to %s" % (upper_lat, lower_lat))
    print ("lng from %s to %s" % (left_lng, right_lng))
    
    grid(float(upper_lat), float(lower_lat), float(left_lng), float(right_lng))
    
    return render_to_response('map/contour_image.html')

def grid (upper_lat, lower_lat, left_lng, right_lng):
    print "generating grid with divsions %f " % GRID_DIVISIONS
    print ("lat from %.6f to %.6f" % (upper_lat, lower_lat))
    print ("lng from %.6f to %.6f" % (left_lng, right_lng))
    
    lat_diff = upper_lat - lower_lat
    lat_spacing = lat_diff / GRID_DIVISIONS
    
    lng_diff = left_lng - right_lng
    lng_spacing = lng_diff / GRID_DIVISIONS
    
    lats = []
    lngs = []
    for i in range(GRID_DIVISIONS):
        lats.append(upper_lat - (i * lat_spacing))
        lngs.append(right_lng - (i * lng_spacing))
    
    #print lats
    #print lngs
    
    coords = []
    
    for lat in lats:
        for lng in lngs:
            coords.append({'lat':lat,'lng':lng})

    string_coords = ""
    list_coords = []
    for coord in coords:
        string_coords = string_coords + ('%.5f' % coord['lat'])  + ',' + ('%.5f' % coord['lng']) + '\n'
        list_coords.append(coord['lat'])
        list_coords.append(coord['lng'])
    
    #print string_coords
    print "--------"
    data = compress(list_coords, 5)
    url = "http://platform.beta.mapquest.com/elevation/v1/getElevationProfile?key=Fmjtd%7Cluu7n1u2nq%2C2l%3Do5-5rbad&shapeFormat=cmp&latLngCollection="
    #print data
    full_url = url + data
    #print full_url
    
    response = urllib2.urlopen(full_url)
    print "*************"
    resp_string = response.read()
    print resp_string
    results = json.loads(resp_string)
    #pp = pprint.PrettyPrinter(indent=4)
    #pp.pprint(results['elevationProfile'])
    
    hts = []
    
    #for result in results['elevationProfile']:
    #    hts.append(result['height'])

    index = 0
    for lat in lats:
        row = []
        for lng in lngs:
            row.append(results['elevationProfile'][index]['height'])
            index = index + 1
        hts.append(row)
    print hts
    
    plt.figure(facecolor='0000')

    CS = plt.contour(lats, lngs, np.array(hts), 6, colors='w',)


    plt.axes().set_axis_off()

    plt.savefig('test.png', bbox_inches='tight', transparent='True')

    
def compress(points, precision):
   oldLat = 0
   oldLng = 0
   len_pts = len(points)
   index = 0
   encoded = ''
   precision = pow(10, precision)
   while (index < len_pts):
      #  Round to N decimal places
      lat = int(round(points[index] * precision));
      index = index + 1
      lng = int(round(points[index] * precision));
      index = index + 1

      #  Encode the differences between the points
      encoded += encodeNumber(lat - oldLat);
      encoded += encodeNumber(lng - oldLng);
      
      oldLat = lat;
      oldLng = lng;
   
   return encoded


def encodeNumber(num):
   num = num << 1
   if (num < 0):
      num = ~(num)
   
   encoded = ''
   while (num >= 0x20):
      encoded += chr((0x20 | (num & 0x1f)) + 63)
      num >>= 5
   
   encoded += chr(num + 63)
   return encoded
