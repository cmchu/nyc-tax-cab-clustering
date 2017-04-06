# NYC Taxi Cab Clustering

In this project, the goal was to cluster the New York City Green taxi cab data using different clustering methods in order to answer certain questions. These questions include:

1. What are the top 5 locations which are the origin points of trips?
2. What are the top 5 locations which are the termination points of trips?
3. What are the top 3 time periods of the day that generate the most pick-ups?
4. If we define lucrative trips as generating the highest fare for least amount of time spent, what are the top 5 locations for the origin of the most lucrative trips?
5. If we define lucrative trips as generating the highest fare for least amount of time spent, what are the top 5 locations for the termination of the most lucrative trips?

Additionally, Google Maps API was used in order to approximately outline the top 5 locations in each respective question.

## Methods

For questions 1, 2, 4, and 5, I chose to use DBSCAN as the clustering algorithm because it seeks compactness rather than connectivity. In this case, in which we are trying to find top locations of origins and terminations of trips, it makes more sense to have locations that are compact, rather than locations that could span 1 mile. This is the reasoning behind choosing DBSCAN over clustering algorithms, such as hierarchical and spectral clustering. Additionally, I chose DBSCAN over K-means because DBSCAN allows for outliers, whereas K-means does not. I believe outliers can occur frequently in this type of data.

For question 3, I chose to use K-means as the clustering algorithm because we are only clustering on 1 variable. Additionally, this 1 variable is time. Therefore, we do not have to worry about outliers or odd cluster shapes.

## Data

Data can be found at http://www.nyc.gov/html/tlc/html/about/trip_record_data.shtml. I only analyzed the Green data of March 2016.

## File descriptions

nyc_taxi_cab_clustering.py contains all of the code used in clustering the data, as well as in printing and displaying (using the Google Maps API) the answers to the above questions.

temp.html is called within the nyc_taxi_cab_clustering.py file and is used to display the top locations using the Google Maps API.
