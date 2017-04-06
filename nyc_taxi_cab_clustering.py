import pandas as pd
from sklearn import cluster
import numpy as np
import os, webbrowser, time

def google_maps_api_javascript(lat, lng, points, label):
    """
    creates the javascript that displays the cluster locations using the google maps api
    """
    beginning = """<!DOCTYPE html>
                <html>
                  <head>
                    <meta name="viewport" content="initial-scale=1.0, user-scalable=no">
                    <meta charset="utf-8">
                    <title>Simple Polylines</title>
                    <style>
                      /* Always set the map height explicitly to define the size of the div
                       * element that contains the map. */
                      #map {
                        height: 100%;
                      }
                      /* Optional: Makes the sample page fill the window. */
                      html, body {
                        height: 100%;
                        margin: 0;
                        padding: 0;
                      }
                    </style>
                  </head>
                  <body>
                    <div id="map"></div>
                    <script>
                      function initMap() {
                        var myLatLng = """
    middle1 = "{lat:%f, lng:%f};" % (lat, lng)
    middle2 = """var map = new google.maps.Map(document.getElementById('map'), {
                          zoom: 13,
                          center: myLatLng
                        });

                        var BoundaryCoordinates = ["""
    latlng = []
    for point in points:
        latlng += ["{lat: %f, lng: %f}" % (point[0], point[1])]
    middle3 = ',\n'.join(latlng)
    middle4 ="""];
                        var Boundary = new google.maps.Polyline({
                          path: BoundaryCoordinates,
                          geodesic: true,
                          strokeColor: '#FF0000',
                          strokeOpacity: 1.0,
                          strokeWeight: 2
                        });

                        var marker = new google.maps.Marker({
                              position: myLatLng,
                              map: map,
                              title: 'Top Origin Points of Trips',"""
    middle5 = "label: '%s'" % label
    middle6 = """});"""
    middle7 = """var bounds = new google.maps.LatLngBounds();
        for (var i = 0; i < BoundaryCoordinates.length; i++) {
            bounds.extend(BoundaryCoordinates[i]);
        }"""
    end = """Boundary.setMap(map);
                        map.fitBounds(bounds);
                      }
                    </script>
                    <script async defer
                    src="https://maps.googleapis.com/maps/api/js?key=AIzaSyBEQOGJSL_eVuwali6jKk1k1gZxtk-l68k&callback=initMap">
                    </script>
                  </body>
                </html>"""
    return beginning + middle1 + middle2 + middle3 + middle4 + middle5 + middle6 + middle7 + end

def get_sec(time_str):
    """
    converts a string in format %H:%M:%S into number of seconds since midnight
    """
    h, m, s = time_str.split(':')
    return int(h) * 3600 + int(m) * 60 + int(s)

# taken from http://tomswitzer.net/2010/03/graham-scan/
# these functions create a convex hull polygon from a set of points
TURN_LEFT, TURN_RIGHT, TURN_NONE = (1, -1, 0)

def turn(p, q, r):
    return cmp((q[0] - p[0])*(r[1] - p[1]) - (r[0] - p[0])*(q[1] - p[1]), 0)

def _keep_left(hull, r):
    while len(hull) > 1 and turn(hull[-2], hull[-1], r) != TURN_LEFT:
            hull.pop()
    if not len(hull) or hull[-1] != r:
        hull.append(r)
    return hull

def convex_hull(points):
    """Returns points on convex hull of an array of points in CCW order."""
    points = sorted(points)
    l = reduce(_keep_left, points, [])
    u = reduce(_keep_left, reversed(points), [])
    return l.extend(u[i] for i in xrange(1, len(u) - 1)) or l

# read in data
greentaxis_df = pd.read_csv('green_tripdata_2016-03.csv')

#######################################################################
#### Question 2 - Top 5 locations which are origin points of trips ####
#######################################################################
print
print "Question 2"

# remove origin points with latitude=0, longitude=0
greentaxis_df = greentaxis_df[(greentaxis_df.Pickup_latitude != 0) & (greentaxis_df.Pickup_longitude != 0)]
# remove termination points with latitude=0, longitude=0
greentaxis_df = greentaxis_df[(greentaxis_df.Dropoff_latitude != 0) & (greentaxis_df.Dropoff_longitude != 0)]

# DBSCAN to get origin location clusters
origin_pts_clusters_df = greentaxis_df.ix[:,['Pickup_latitude', 'Pickup_longitude']]
dbscan_clusters = cluster.DBSCAN(eps=0.00008, min_samples=50)
dbscan_clusters.fit(np.array(origin_pts_clusters_df))
origin_pts_clusters_df = greentaxis_df.ix[:,['Pickup_latitude', 'Pickup_longitude']]
origin_pts_clusters_df['cluster'] = dbscan_clusters.labels_

# getting top 5 origin location clusters
cluster_percentage = origin_pts_clusters_df['cluster'].value_counts()/float(origin_pts_clusters_df.shape[0])
cluster_percentage = cluster_percentage.drop([-1])
top5origin_clusters = cluster_percentage.index[0:5].tolist()

# printing percentage of trips originating from each cluster location and displaying each cluster location on google maps
labels = ['1st', '2nd', '3rd', '4th', '5th']
for i in range(0,5):
    time.sleep(5)
    print labels[i] + " best origin location"
    # printing percentage of trips originating from this cluster location
    print "\t" + str(cluster_percentage[top5origin_clusters[i]]*100) + "%"
    # get mean latitude/longitude and convex hull polygon for each of the top 5 clusters for origin location
    cluster_df = origin_pts_clusters_df[origin_pts_clusters_df.cluster == top5origin_clusters[i]]
    cluster_df = cluster_df.ix[:,['Pickup_latitude', 'Pickup_longitude']]
    mean_lat = np.mean(cluster_df.Pickup_latitude)
    mean_lng = np.mean(cluster_df.Pickup_longitude)
    print "\t" + str(mean_lat) + ", " + str(mean_lng)
    polyline_points = convex_hull(np.array(cluster_df).tolist())
    polyline_points += [polyline_points[0]]
    # using google maps API to display mean latitude/longitude for each of the top 5 clusters for origin location
    html = google_maps_api_javascript(mean_lat, mean_lng, polyline_points, 'Q2: ' + labels[i] + ', ' + str(round(cluster_percentage[top5origin_clusters[i]]*100, 2)) + '%')
    path = os.path.abspath('temp.html')
    url = 'file://' + path

    with open(path, 'w') as f:
        f.write(html)
    webbrowser.open(url)

############################################################################
#### Question 3 - Top 5 locations which are termination points of trips ####
############################################################################
print
print "Question 3"

# DBSCAN to get termination location clusters
termination_pts_clusters_df = greentaxis_df.ix[:, ['Dropoff_latitude', 'Dropoff_longitude']]
dbscan_clusters = cluster.DBSCAN(eps=0.00008, min_samples=20)
dbscan_clusters.fit(np.array(termination_pts_clusters_df))
termination_pts_clusters_df['cluster'] = dbscan_clusters.labels_

# getting top 5 termination location clusters
cluster_percentage = termination_pts_clusters_df['cluster'].value_counts() / float(termination_pts_clusters_df.shape[0])
cluster_percentage = cluster_percentage.drop([-1])
top5termination_clusters = cluster_percentage.index[0:5].tolist()

# printing percentage of trips terminating at each cluster location and displaying each cluster location on google maps
labels = ['1st', '2nd', '3rd', '4th', '5th']
for i in range(0, 5):
    time.sleep(5)
    print labels[i] + " best termination location"
    # printing percentage of trips terminating at this cluster location
    print "\t" + str(cluster_percentage[top5termination_clusters[i]]*100) + "%"
    # get mean latitude/longitude and convex hull polygon for each of the top 5 clusters for termination location
    cluster_df = termination_pts_clusters_df[termination_pts_clusters_df.cluster == top5termination_clusters[i]]
    cluster_df = cluster_df.ix[:,['Dropoff_latitude', 'Dropoff_longitude']]
    mean_lat = np.mean(cluster_df.Dropoff_latitude)
    mean_lng = np.mean(cluster_df.Dropoff_longitude)
    print "\t" + str(mean_lat) + ", " + str(mean_lng)
    polyline_points = convex_hull(np.array(cluster_df).tolist())
    polyline_points += [polyline_points[0]]
    # using google maps API to display mean latitude/longitude for each of the top 5 clusters for termination location
    html = google_maps_api_javascript(mean_lat, mean_lng, polyline_points, 'Q3: ' + labels[i] + ', ' + str(round(cluster_percentage[top5termination_clusters[i]]*100, 2)) + '%')
    path = os.path.abspath('temp.html')
    url = 'file://' + path

    with open(path, 'w') as f:
        f.write(html)
    webbrowser.open(url)

#######################################################################
#### Question 4 - Top 3 time periods of the day with most pick-ups ####
#######################################################################
print
print "Question 4"

# converting lpep_pickup_datetime field to number of seconds since midnight
greentaxis_df['lpep_pickup_datetime'] = pd.to_datetime(greentaxis_df['lpep_pickup_datetime'])
pickup_hour_min_sec = [date.strftime('%H:%M:%S') for date in greentaxis_df['lpep_pickup_datetime']]
pickup_seconds = [[get_sec(time_str)] for time_str in pickup_hour_min_sec]

# performing K-means clustering
kmeans_clusters = cluster.KMeans(n_clusters=20, random_state=5)
kmeans_clusters.fit(pickup_seconds)
pickup_seconds_clusters_df = pd.DataFrame(pickup_seconds, columns=["pickup_seconds"])
pickup_seconds_clusters_df['cluster'] = kmeans_clusters.labels_

# getting top 3 clusters of time periods of the day with most pick-ups
top3seconds_clusters = pickup_seconds_clusters_df['cluster'].value_counts().index[0:3]

# printing the top 3 time periods of the day with most pick-ups
labels = ['1st', '2nd', '3rd']
for i in range(0,3):
    print labels[i] + ' best time period'
    cluster_df = pickup_seconds_clusters_df[pickup_seconds_clusters_df.cluster == top3seconds_clusters[i]]
    min_seconds = min(cluster_df.pickup_seconds)
    min_minute, min_second = divmod(min_seconds, 60)
    min_hour, min_minute = divmod(min_minute, 60)
    max_seconds = max(cluster_df.pickup_seconds)
    max_minute, max_second = divmod(max_seconds, 60)
    max_hour, max_minute = divmod(max_minute, 60)
    print "\t%d:%02d:%02d to %d:%02d:%02d" % (min_hour, min_minute, min_second, max_hour, max_minute, max_second)

############################################################
#### Question 5 - Top 5 most lucrative origin locations ####
############################################################
print
print "Question 5"

# getting the trip length in seconds by subtracting the pickup time from the dropoff time
greentaxis_df['Lpep_dropoff_datetime'] = pd.to_datetime(greentaxis_df['Lpep_dropoff_datetime'])
greentaxis_df['trip_length_seconds'] = (greentaxis_df['Lpep_dropoff_datetime']-greentaxis_df['lpep_pickup_datetime']).astype('timedelta64[s]')

# getting the lucrativeness of a trip by dividing fare amount by trip length in seconds
greentaxis_df['lucrativeness'] = greentaxis_df['Fare_amount']/greentaxis_df['trip_length_seconds']

# removing NaN lucrativeness values
greentaxis_df = greentaxis_df.replace([np.inf,-np.inf], np.nan).dropna(subset=['lucrativeness'])

# DBSCAN to get origin location / lucrativeness clusters
origin_pts_lucrative_clusters_df = greentaxis_df.ix[:,['Pickup_latitude', 'Pickup_longitude', 'lucrativeness']]
dbscan_clusters = cluster.DBSCAN(eps=0.0005, min_samples=5)
dbscan_clusters.fit(np.array(origin_pts_lucrative_clusters_df))
origin_pts_lucrative_clusters_df['cluster'] = dbscan_clusters.labels_

# getting an ordered index from most lucrative origin location clusters to least lucrative
lucrative_origin_clusters = origin_pts_lucrative_clusters_df.groupby(['cluster'])['lucrativeness'].agg(lambda x: np.mean(x)).sort_values(ascending=False)
lucrative_origin_clusters.drop([-1], inplace=True)
lucrative_origin_clusters_index = lucrative_origin_clusters.index[:].tolist()

# displaying each of the top 5 most lucrative origin cluster locations
# (the same location appears three times in a row in top 5 - they are clustered separately because the difference in lucrativeness is large enough)
# this code skips the repeats of locations and only prints a location once
labels = ['1st', '2nd', '3rd', '4th', '5th']
count = 0
prev_mean_lat = 0
prev_mean_lng = 0
i = 0
while count < 5:
    time.sleep(5)
    # get mean latitude/longitude for each of the top 5 most lucrative origin cluster locations
    cluster_df = origin_pts_lucrative_clusters_df[origin_pts_lucrative_clusters_df.cluster == lucrative_origin_clusters_index[i]]
    cluster_df = cluster_df.ix[:, ['Pickup_latitude', 'Pickup_longitude']]
    mean_lat = np.mean(cluster_df.Pickup_latitude)
    mean_lng = np.mean(cluster_df.Pickup_longitude)
    if abs(mean_lat - prev_mean_lat) > .001 and abs(mean_lng - prev_mean_lng) > .001:
        print labels[count] + " best origin location"
        print "\t" + str(lucrative_origin_clusters[lucrative_origin_clusters_index[i]])
        print "\t" + str(mean_lat) + ", " + str(mean_lng)
        # get convex hull polygon for each of the top 5 most lucrative origin cluster locations
        polyline_points = convex_hull(np.array(cluster_df).tolist())
        polyline_points += [polyline_points[0]]
        # using google maps API to display mean latitude/longitude for each of the top 5 most lucrative origin cluster locations
        html = google_maps_api_javascript(mean_lat, mean_lng, polyline_points, 'Q5: ' + labels[count])
        path = os.path.abspath('temp.html')
        url = 'file://' + path

        with open(path, 'w') as f:
            f.write(html)
        webbrowser.open(url)

        prev_mean_lat = mean_lat
        prev_mean_lng = mean_lng
        count += 1
    i += 1

#################################################################
#### Question 6 - Top 5 most lucrative termination locations ####
#################################################################
print
print "Question 6"

# DBSCAN to get origin location / lucrativeness clusters
termination_pts_lucrative_clusters_df = greentaxis_df.ix[:,['Dropoff_latitude', 'Dropoff_longitude', 'lucrativeness']]
dbscan_clusters = cluster.DBSCAN(eps=0.0005, min_samples=5)
dbscan_clusters.fit(np.array(termination_pts_lucrative_clusters_df))
termination_pts_lucrative_clusters_df['cluster'] = dbscan_clusters.labels_

# getting an ordered index from most lucrative termination location clusters to least lucrative
lucrative_termination_clusters = termination_pts_lucrative_clusters_df.groupby(['cluster'])['lucrativeness'].agg(lambda x: np.mean(x)).sort_values(ascending=False)
lucrative_termination_clusters.drop([-1], inplace=True)
lucrative_termination_clusters_index = lucrative_termination_clusters.index[:].tolist()

# displaying each of the top 5 most lucrative termination cluster locations
# (the same location appears three times in a row in top 5 - they are clustered separately because the difference in lucrativeness is large enough)
# this code skips the repeats of locations and only prints a location once
labels = ['1st', '2nd', '3rd', '4th', '5th']
count = 0
prev_mean_lat = 0
prev_mean_lng = 0
i = 0
while count < 5:
    time.sleep(5)
    # get mean latitude/longitude for each of the top 5 most lucrative termination cluster locations
    cluster_df = termination_pts_lucrative_clusters_df[termination_pts_lucrative_clusters_df.cluster == lucrative_termination_clusters_index[i]]
    cluster_df = cluster_df.ix[:, ['Dropoff_latitude', 'Dropoff_longitude']]
    mean_lat = np.mean(cluster_df.Dropoff_latitude)
    mean_lng = np.mean(cluster_df.Dropoff_longitude)
    if abs(mean_lat - prev_mean_lat) > .001 and abs(mean_lng - prev_mean_lng) > .001:
        print labels[count] + " best termination location"
        print "\t" + str(lucrative_termination_clusters[lucrative_termination_clusters_index[i]])
        print "\t" + str(mean_lat) + ", " + str(mean_lng)
        # get convex hull polygon for each of the top 5 most lucrative termination cluster locations
        polyline_points = convex_hull(np.array(cluster_df).tolist())
        polyline_points += [polyline_points[0]]
        # using google maps API to display mean latitude/longitude for each of the top 5 most lucrative termination cluster locations
        html = google_maps_api_javascript(mean_lat, mean_lng, polyline_points, 'Q6: ' + labels[count])
        path = os.path.abspath('temp.html')
        url = 'file://' + path

        with open(path, 'w') as f:
            f.write(html)
        webbrowser.open(url)

        prev_mean_lat = mean_lat
        prev_mean_lng = mean_lng
        count += 1
    i += 1


