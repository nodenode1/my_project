import pandas as pd
from sklearn.cluster import KMeans

music_data = pd.read_csv("SpotifyFeatures.csv")

ranged_music_data = music_data[["danceability", "energy"]]

ranged_music_data_values = ranged_music_data.values

kmeans = KMeans(n_clusters = 8).fit(ranged_music_data_values)

kmeans.labels_

ranged_music_data.loc[:, "cluster_id"] = kmeans.labels_

ranged_music_data.to_csv("Temp_Ranged_SpotifyFeatures.csv")

print("--------------------------------------------------------------------------")
print("Finished Your Clustering")
