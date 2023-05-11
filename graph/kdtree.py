import geopandas as gpd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.manifold import MDS
from sklearn.neighbors import KDTree
from sklearn.metrics import pairwise_distances


class KDTreeNeighbors:
    tree = []
    neighbourhoods = []

    T = []

    def find_nearest_neighborhood(self, lat, lon):
        """Trova il quartiere più vicino alla latitudine e longitudine fornite."""
        # ricerca dei quartieri più vicini
        distances, indices = self.tree.query([[lat, lon]], k=1)

        # ottiene l'indice del quartiere più vicino
        nearest_index = indices[0][0]

        # ritorna il nome del quartiere più vicino
        return self.neighbourhoods.iloc[nearest_index]['AREA_NAME']

    def create_tree(self):
        # Carichiamo il file GeoJSON con i quartieri e le loro coordinate latitudine e longitudine
        neighborhoods = gpd.read_file('datasets/original_neighbourhoods.geojson')
        neighborhoods["AREA_NAME"] = neighborhoods["AREA_NAME"].str.replace(r"\s*\(\d+\)$", "", regex=True)

        # crea un array di coordinate latitudine e longitudine
        self.T = np.array(neighborhoods[['LATITUDE', 'LONGITUDE']])

        # crea un albero di ricerca spaziale
        tree = KDTree(self.T)

        self.neighbourhoods = neighborhoods
        self.tree = tree
        return tree

    def plot_neighborhood(self, lat, lon):
        # visualizza tutti i quartieri
        fig, ax = plt.subplots(figsize=(10, 10))
        self.neighbourhoods.plot(ax=ax, color='lightgray', edgecolor='white')

        # visualizza il quartiere più vicino a un incidente specifico
        # lat, lon = 43.6532, -79.3832 # esempio di latitudine e longitudine per un incidente
        nearest_neighborhood = self.find_nearest_neighborhood(lat, lon)
        nearest_polygon = self.neighbourhoods[self.neighbourhoods['AREA_NAME'] == nearest_neighborhood]
        nearest_polygon.plot(ax=ax, color='red', edgecolor='white', linewidth=3)

        # visualizza il punto corrispondente alle coordinate passate in ingresso
        ax.scatter(lon, lat, color='blue', marker='*', s=300)

        plt.title('Nearest neighborhood: ' + nearest_neighborhood)
        plt.xlabel('Longitude')
        plt.ylabel('Latitude')
        # plt.show()
        return nearest_neighborhood

    def plot_graph(self, neighbourhoods):
        fig, ax = plt.subplots(figsize=(10, 10))
        neighbourhoods.plot(ax=ax, color='lightgray', edgecolor='white')

        # Aggiungi una griglia e imposta gli intervalli delle etichette per gli assi x e y
        ax.set_xticks(
            np.arange(np.floor(neighbourhoods.total_bounds[0]), np.ceil(neighbourhoods.total_bounds[2]), 0.05),
            minor=True)
        ax.set_yticks(
            np.arange(np.floor(neighbourhoods.total_bounds[1]), np.ceil(neighbourhoods.total_bounds[3]), 0.05),
            minor=True)
        ax.grid(which='minor', linestyle='--', alpha=0.5)

        plt.show()

    def plot_tree_2d(self, lat, lon):
        # Ottieni le coordinate dei punti nell'albero di ricerca spaziale
        X = self.T

        # Calcola le distanze euclidee tra i punti
        dist_matrix = pairwise_distances(X)

        # Applica la tecnica di visualizzazione MDS per proiettare i punti in 2D
        mds = MDS(n_components=2, dissimilarity='precomputed')
        X_mds = mds.fit_transform(dist_matrix)

        # Trova il nearest neighborhood per le coordinate specificate
        nearest_neighborhood = self.find_nearest_neighborhood(lat, lon)

        # Visualizza i punti proiettati in un grafico 2D, evidenziando il nuovo punto e il nearest neighborhood
        fig, ax = plt.subplots(figsize=(10, 10))
        ax.scatter(lon, lat, color='red', s=50, label='New Point')
        ax.scatter(X_mds[self.neighbourhoods[self.neighbourhoods['AREA_NAME'] == nearest_neighborhood].index.values, 0],
                   X_mds[self.neighbourhoods[self.neighbourhoods['AREA_NAME'] == nearest_neighborhood].index.values, 1],
                   color='orange', s=50, label='Nearest Neighborhood')
        ax.scatter(X_mds[:, 0], X_mds[:, 1], s=5, alpha=0.1)
        plt.legend()
        plt.show()

    def get_neighbourhoods(self):
        return self.neighbourhoods


if __name__ == '__main__':
    kdtree = KDTree()
    kdtree.create_tree()
    kdtree.plot_graph(kdtree.neighbourhoods)
    lat, lon = 43.6532, -79.3832  # esempio di latitudine e longitudine per un incidente
    kdtree.plot_neighborhood(lat, lon)
    kdtree.plot_graph_2d(kdtree.tree)
