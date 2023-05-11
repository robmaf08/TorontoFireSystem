import numpy as np  # library to handle data in a vectorized manner
import networkx as nx
import pandas as pd  # library for data analsysis
import heapq
import geopandas as gpd  # to strore geospatial data
import matplotlib.pyplot as plt  # Import Matplotlib for visualizations
import math
import pickle
import os
from itertools import permutations

GRAPH_MODEL_PATH = './graph/graph.pkl'


class Graph:
    G = []
    name_to_number = []
    name_to_number_stations = []
    toronto_gdf = []
    node_colors = []

    def __init__(self, tree):
        self.G = []
        self.name_to_number = []
        self.name_to_number_stations = []
        self.toronto_gdf = []
        self.node_colors = []

        if os.path.exists('./graph/graph.pkl') is False:
            self.create_graph()
            self.add_fire_stations(tree)
            self.save_graph()
        else:
            self.load_graph()

    def save_graph(self):
        with open(GRAPH_MODEL_PATH, 'wb') as file:
            pickle.dump(self, file)

    def load_graph(self):
        with open(GRAPH_MODEL_PATH, 'rb') as file:
            loaded_instance = pickle.load(file)
            self.G = loaded_instance.G
            self.name_to_number = loaded_instance.name_to_number
            self.name_to_number_stations = loaded_instance.name_to_number_stations
            self.toronto_gdf = loaded_instance.toronto_gdf
            self.node_colors = loaded_instance.node_colors

    # Convertes grades in radiant
    def radians(self, x):
        return x * math.pi / 180

    # Returns the distance in meters of two coords with haversine formula
    def haversine(self, lat1, lon1, lat2, lon2):
        # Earth radius in meters
        R = 6371000
        dLat = self.radians(lat2 - lat1)
        dLon = self.radians(lon2 - lon1)
        lat1 = self.radians(lat1)
        lat2 = self.radians(lat2)
        a = math.sin(dLat / 2) * math.sin(dLat / 2) + \
            math.sin(dLon / 2) * math.sin(dLon / 2) * math.cos(lat1) * math.cos(lat2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        d = R * c
        return d

    def plot_graph(self):
        # Drawing graph
        plt.figure(figsize=(50, 50))
        pos = nx.get_node_attributes(self.G, "pos")
        nx.draw_networkx(self.G, pos=pos, with_labels=True)

        # Add the labels to egde's weight
        labels = nx.get_edge_attributes(self.G, "weight")
        nx.draw_networkx_edge_labels(self.G, pos=pos, edge_labels=labels)
        nx.draw_networkx(self.G, pos=pos, node_color=self.node_colors, with_labels=True)

        plt.show()

    def create_graph(self):
        # Read GEOJSON file to a Geopandas dataframe
        toronto_gdf = gpd.read_file(
            "datasets/original_neighbourhoods.geojson")
        # print(toronto_gdf.head())  # Display initial dataframe to see what outcome is
        toronto_gdf = toronto_gdf.iloc[:, 5:]  # Slice dataframe for only relevant attributes
        # Rename Area_Long_Code as it is same as Neighbourhood ID
        toronto_gdf.rename(columns={'AREA_LONG_CODE': 'Neighbourhood ID'},
                           inplace=True)
        # Drop irrelevant columns
        toronto_gdf.drop(labels=['AREA_DESC', 'OBJECTID', 'X', 'Y'],
                         axis=1, inplace=True)
        # Remove the numbers of after neighbourhood
        toronto_gdf["AREA_NAME"] = toronto_gdf["AREA_NAME"].str.replace(r"\s*\(\d+\)$", "", regex=True)
        neighborhood_names = toronto_gdf["AREA_NAME"].tolist()
        neighborhood_numbers = dict(zip(toronto_gdf["Neighbourhood ID"], toronto_gdf.index))
        name_to_number = dict(zip(neighborhood_names, neighborhood_numbers))
        self.name_to_number = name_to_number
        self.toronto_gdf = toronto_gdf

        # Create an empty graph
        self.G = nx.Graph()

        # Adding node for each neighbourhood
        for i, row in toronto_gdf.iterrows():
            name = row["AREA_NAME"]
            number = name_to_number[name]
            self.G.add_node(number, pos=(row["LONGITUDE"], row["LATITUDE"]))

        # Connecting adiacent nodes
        for i, row1 in toronto_gdf.iterrows():
            name1 = row1["AREA_NAME"]
            number_row1 = name_to_number[name1]
            boundary1 = row1["geometry"].boundary

            for j, row2 in toronto_gdf.iterrows():
                name2 = row2["AREA_NAME"]
                number_row2 = name_to_number[name2]

                if number_row1 == number_row2:
                    continue

                boundary2 = row2["geometry"].boundary
                common_boundary = boundary1.intersection(boundary2)

                if common_boundary.length > 0:
                    dist = self.haversine(row1["LATITUDE"], row1["LONGITUDE"], row2["LATITUDE"], row2["LONGITUDE"])
                    self.G.add_edge(number_row1, number_row2, weight=round(dist, 3))

        # self.plot_graph()

    def find_nearest_neighborhood2(self, tree, lat, lon, df):
        # Finding the closest neighbourhood to a specific latitude and longitude
        distances, indices = tree.tree.query([[lat, lon]], k=1)
        # Get its index
        nearest_index = indices[0][0]
        # Returns the neighbour's name
        return df.iloc[nearest_index]['AREA_NAME']

    def add_fire_stations(self, tree):
        # Reading dataset of fire stations location
        fire_stations = pd.read_csv('datasets/fire-station-locations.csv')
        for index, row in fire_stations.iterrows():
            lat, lon = row['Latitude'], row['Longitude']
            # Finding the neighbour close to the coordinates
            nearest_neighborhood = tree.find_nearest_neighborhood(lat, lon)
            fire_stations.at[index, 'Neighbourhood'] = nearest_neighborhood

        # Remove the number after the neighbourhood name
        fire_stations["Neighbourhood"] = fire_stations["Neighbourhood"].str.replace(r"\s*\(\d+\)$", "", regex=True)
        stations_number = []
        for index, row in fire_stations.iterrows():
            lat, lon = row['Latitude'], row['Longitude']

            # Find closest neighbour to incident's coords
            nearest_neighborhood = self.find_nearest_neighborhood2(tree, lat, lon, self.toronto_gdf)

            # Add fire station to the neighbour found
            neighborhood_node = self.name_to_number[nearest_neighborhood]
            station_node = "Station " + str(row['STATION'])
            self.name_to_number_stations.append(station_node)
            self.G.add_node(station_node, pos=(lon, lat))

            # Calcultating distance from neighbourhood and fire station
            lat1, lon1 = self.G.nodes[neighborhood_node]['pos']
            lat2, lon2 = self.G.nodes[station_node]['pos']
            distance = self.haversine(lat1, lon1, lat2, lon2)

            # Adding edge with distance weight
            self.G.add_edge(neighborhood_node, station_node, weight=distance)

        # Making stations as red node and add edges
        node_colors = []
        for node in self.G.nodes():
            if isinstance(node, str) and node.startswith("Station"):
                node_colors.append("red")
            elif isinstance(node, int) and str(node).startswith("Station"):
                node_colors.append("red")
            else:
                node_colors.append("lightgray")

        self.node_colors = node_colors

    def dijkstra_search(self, start, end):
        frontier = []
        heapq.heappush(frontier, (0, start))
        came_from = {}
        cost_so_far = {}
        came_from[start] = None
        cost_so_far[start] = 0

        while frontier:
            current = heapq.heappop(frontier)[1]

            if current == end:
                break

            for next_node in self.G.neighbors(current):
                new_cost = cost_so_far[current] + self.G[current][next_node]['weight']
                if next_node not in cost_so_far or new_cost < cost_so_far[next_node]:
                    cost_so_far[next_node] = new_cost
                    priority = new_cost
                    heapq.heappush(frontier, (priority, next_node))
                    came_from[next_node] = current

        path = []
        current = end
        while current != start:
            path.append(current)
            current = came_from[current]
        path.append(start)
        path.reverse()

        return path

    def path_length(self, path):
        total_length = 0

        for i in range(len(path) - 1):
            start_node = path[i]
            end_node = path[i + 1]
            edge_weight = self.G[start_node][end_node]['weight']
            total_length += edge_weight

        return total_length

    def tsp_search(self, start, target_nodes):
        shortest_path = None
        shortest_path_length = float('inf')

        # Calculating all permutations of target nodes
        target_permutations = permutations(target_nodes)

        for perm in target_permutations:
            current_path = [start]
            current_path_length = 0

            # Calculating path between each couple of consecutive node in the permutation
            for i in range(len(perm)):
                if i == 0:
                    start_node = start
                else:
                    start_node = perm[i - 1]

                end_node = perm[i]

                path = self.dijkstra_search(start_node, end_node)
                current_path_length += self.path_length(path)
                current_path += path[1:]

            # Calculating path to return to starting node
            path_to_start = self.dijkstra_search(perm[-1], start)
            current_path_length += self.path_length(path_to_start)
            current_path += path_to_start[1:]

            # Checking if current path is shorter than the previous shortest path
            if current_path_length < shortest_path_length:
                shortest_path = current_path
                shortest_path_length = current_path_length

        return shortest_path

    def plot_path(self, path):
        # print(path)

        node_colors = []
        path_edges = list(zip(path, path[1:]))
        # print(path_edges)

        # Calculating the final weight of path lenght in km
        total_weight = sum([self.G[edge[0]][edge[1]]["weight"] for edge in path_edges])
        print(f"Distanza totale: {total_weight / 1000} km")

        # Creating a dictionary for counting the edge occurences in the path
        edge_count = {}
        for edge in path_edges:
            if edge in edge_count:
                edge_count[edge] += 1
            elif edge[::-1] in edge_count:
                edge_count[edge[::-1]] += 1
            else:
                edge_count[edge] = 1

        # Defining border, colors and lenght
        edge_colors = []
        widths = []
        for edge in self.G.edges():
            if edge in edge_count:
                count = edge_count[edge]
            elif edge[::-1] in edge_count:
                count = edge_count[edge[::-1]]
            else:
                count = 0

            if count == 1:
                edge_colors.append("orange")
                widths.append(5)
            elif count > 1:
                edge_colors.append("red")
                widths.append(3 * count)
            else:
                edge_colors.append("gray")
                widths.append(2)

        # Drawing graph
        pos = nx.get_node_attributes(self.G, "pos")
        node_sizes = [20 if (isinstance(node, str) and node.startswith("s")) else 200 for node in self.G.nodes()]
        plt.figure(figsize=(30, 20))
        nx.draw_networkx(self.G, pos=pos, node_color=self.node_colors, node_size=node_sizes,
                         edge_color=edge_colors, width=widths)

        # Adding legend
        import matplotlib.patches as mpatches
        red_patch = mpatches.Patch(color='red', label='Fire stations')
        gray_patch = mpatches.Patch(color='lightgray', label='Neighbourhoods')
        plt.legend(handles=[red_patch, gray_patch], loc='lower right', fontsize=18)

        # Adding total weight as text in the visualization
        plt.text(0.05, 0.95, f"Distanza totale: {total_weight / 1000:.2f} km", transform=plt.gca().transAxes, fontsize=18)
        plt.show()

    def plot_map_graph(self, tree, path):
        pos = nx.get_node_attributes(self.G, 'pos')
        path_edges = list(zip(path, path[1:]))
        total_weight = sum([self.G[edge[0]][edge[1]]["weight"] for edge in path_edges])
        print(f"Distanza totale: {total_weight} km")
        # Drawing map
        fig, ax = plt.subplots(figsize=(20, 20))
        tree.neighbourhoods.plot(ax=ax, color='lightgray', edgecolor='white')

        # Defining grahp colors
        edge_colors = []
        for edge in self.G.edges():
            if edge in path_edges or edge[::-1] in path_edges:
                edge_colors.append("green")
            else:
                edge_colors.append("gray")

        for node in self.G.nodes:
            if isinstance(node, str) and node.startswith("s"):
                nx.draw_networkx_nodes(self.G, pos, nodelist=[node], node_size=20, node_color='red')
            elif isinstance(node, int) and str(node).startswith("s"):
                nx.draw_networkx_nodes(self.G, pos, nodelist=[node], node_size=20, node_color='red')
            else:
                nx.draw_networkx_nodes(self.G, pos, nodelist=[node], node_size=100, node_color='gray')

        # Drawing node and edges
        nx.draw_networkx_edges(self.G, pos=pos, width=1.5, alpha=0.8, edge_color=edge_colors)
        nx.draw_networkx_labels(self.G, pos, font_size=10, font_color='black')
        # Adding legend
        import matplotlib.patches as mpatches
        red_patch = mpatches.Patch(color='red', label='Fire stations')
        gray_patch = mpatches.Patch(color='lightgray', label='Neighbourhoods')
        plt.legend(handles=[red_patch, gray_patch], loc='lower right', fontsize=18)
        # Plot map graph
        plt.text(0.05, 0.95, f"Distanza totale: {total_weight:.2f} km", transform=plt.gca().transAxes, fontsize=18)
        plt.show()


"""
    def tsp_search(self, start, target_nodes):
        shortest_path = None
        shortest_path_length = float('inf')

        # Calcola tutte le permutazioni possibili dei nodi target
        target_permutations = permutations(target_nodes)

        for perm in target_permutations:
            current_path = [start]
            current_path_length = 0

            # Calcola il percorso tra ogni coppia di nodi consecutivi nella permutazione
            for i in range(len(perm)):
                if i == 0:
                    start_node = start
                else:
                    start_node = perm[i - 1]

                end_node = perm[i]

                # Usa il tuo algoritmo A* per trovare il percorso tra start_node e end_node
                path = self.astar_search(start_node, end_node)

                # Aggiungi la lunghezza del percorso corrente
                current_path_length += self.path_length(path)

                # Aggiungi il percorso al percorso totale
                current_path += path[1:]

            # Controlla se il percorso corrente è più corto del percorso più breve trovato finora
            if current_path_length < shortest_path_length:
                shortest_path = current_path
                shortest_path_length = current_path_length

        return shortest_path
"""
