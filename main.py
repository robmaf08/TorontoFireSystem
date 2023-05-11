import os
import pandas as pd
import random
from knowledge_base import knowledge_base
from knowledge_base.knowledge_base import KnowledgeBase
from pyswip import Prolog
from utils import menu
from graph.graph import Graph
from graph.kdtree import KDTreeNeighbors
from supervised_learning.estimator import Estimator
from datetime import datetime, timedelta

EXIT_CHOICE = '0'
KNOWLEDGE_BASE_PATH = './knowledge_base/kb.pl'
ID_INCIDENTS_COUNT = 10616
CHOICE_SIMULATE_INCIDENT = '1'
CHOICE_CLOSING_INCIDENT = '2'
CHOICE_KNOWLEDGE_BASE = '3'
CHOICE_PATH_FINDING = '4'


def search_path():
    menu.search_neighbourhoods()


def simulate_availability(kb):
    # Simulating the stations avaiability in a moment
    stations = list(kb.query(f"findall(S, stazione(S, 'Disponibilita', 1), Stazioni)"))
    for station in stations[0]['Stazioni']:
        is_avaiable = random.choice([0, 1])
        kb.retract(f"stazione('{station}', 'Disponibilita', 1)")
        assertz = f"stazione('{station}', 'Disponibilita', {is_avaiable})"
        kb.assertz(assertz)


def simulate_date_incident():
    start_date = datetime(2018, 3, 1, 0, 0, 0)
    end_date = datetime(2018, 3, 2, 0, 0, 0)
    random_date = start_date + timedelta(seconds=random.randint(0, int((end_date - start_date).total_seconds())))
    return random_date.strftime('%Y-%m-%dT%H:%M:%S')


def simulate_arrival_date_incident(tfs_alarm_time_str, min_time, max_time):
    # Convert string in datetime
    tfs_alarm_time = datetime.strptime(tfs_alarm_time_str, '%Y-%m-%dT%H:%M:%S')
    # Generate TFS_Arrival_Time
    tfs_arrival_time = tfs_alarm_time + timedelta(seconds=random.randint(min_time, max_time))
    # Format time in string
    return tfs_arrival_time.strftime('%Y-%m-%dT%H:%M:%S')


def simulate_incident(tree, kb, prolog, graph):
    # Generiamo le coordinate (latitudine e longitudine) dell'incendio
    # lat, lon = 43.651070, -79.457015
    # Coordinata minima e massima per la latitudine e la longitudine
    lat_min = 43.581
    lat_max = 43.855
    lon_min = -79.639
    lon_max = -79.115
    # Genera una latitudine casuale compresa tra lat_min e lat_max
    lat = random.uniform(lat_min, lat_max)
    # Genera una longitudine casuale compresa tra lon_min e lon_max
    lon = random.uniform(lon_min, lon_max)
    print(f"Latitudine: {lat}, Longitudine: {lon}")
    neigh = tree.plot_neighborhood(lat, lon)
    # tree.plot_tree_2d(lat, lon)
    # neigh = tree.plot_graph_2d(lat, lon)
    print("Quartiere: ", neigh)

    # Mostriamo le stazioni disponibili
    stations = list(
        prolog.query("{Stazioni}/(findall(Stazione, stazione(Stazione, 'Disponibilita', 1), Stazioni))"))
    kb.station_avaiability(prolog, True)
    tfs_alarm_time = simulate_date_incident()
    print("TFS_Alarm_Time: ", tfs_alarm_time)

    # Generiamo la possibile causa e il tipo di proprietà dell'incendio
    df = pd.read_csv('datasets/fire_knowledgewn.csv')
    """random_cause = df['Possible_Cause'].sample().values[0]
    print("Random possible cause:", random_cause)"""
    possile_cause = df['Possible_Cause'].sample().values[0]
    property_use = df['Property_Use'].sample().values[0]

    # Assegnazione dell'incendio ad una stazione
    station_assigned = list(
        prolog.query(f"assegna_stazione({lat}, {lon}, '{possile_cause}', '{property_use}', StazioneAssegnata)"))

    print("Possibile causa: ", possile_cause)
    print("Tipo di proprietà coinvolta: ", property_use)
    print(f"Stazione assegnata per l'incendio con ID ({ID_INCIDENTS_COUNT}): ",
          station_assigned[0]['StazioneAssegnata'])
    efficency = list(prolog.query(f"efficienza_stazione('{station_assigned[0]['StazioneAssegnata']}', Efficienza)."))

    print("Efficienza Stazione: ", efficency[0]['Efficienza'])
    query_lat = f"stazione('{station_assigned[0]['StazioneAssegnata']}', 'Latitude', LatStaz)"
    query_lon = f"stazione('{station_assigned[0]['StazioneAssegnata']}', 'Longitude', LonStaz)"
    distance = list(prolog.query(query_lat))
    lat_staz = distance[0]['LatStaz']
    print("Latitudine Stazione: ", lat_staz)
    distance = list(prolog.query(query_lon))
    lon_staz = distance[0]['LonStaz']
    print("Longitudine Stazione: ", lon_staz)
    query_distance = f"distanza_incidente_stazione({lat}, {lon}, '{station_assigned[0]['StazioneAssegnata']}', Distanza)."
    distance = list(prolog.query(query_distance))
    dist_km = distance[0]['Distanza']
    print("Distanza dal luogo dell'incidente: ", dist_km, " km")
    # query = list(kb.query(f"esperienza_tipo_incendio('{station_assigned[0]['StazioneAssegnata']}', '{property_use}', '{possile_cause}', Esperienza)."))
    # print('Esperienza stazione per tipologia di incendio: ', query[0]['Esperienza'])

    print("Quartiere incendio: ", graph.name_to_number[neigh])
    path = G.dijkstra_search(int(graph.name_to_number[neigh]), 's' + station_assigned[0]['StazioneAssegnata'])
    # graph.plot_path(path)

    prolog.retract(f"stazione('{station_assigned[0]['StazioneAssegnata']}', 'Disponibilita', _)")
    assertz = f"stazione('{station_assigned[0]['StazioneAssegnata']}', 'Disponibilita', {0})"
    prolog.assertz(assertz)

    # Registrazione incidente nella base di conoscenza
    assertz = f"incidente('{ID_INCIDENTS_COUNT}', 'TFS_Alarm_Time', '{tfs_alarm_time}')"
    prolog.assertz(assertz)
    prolog.assertz(f"incidente('{ID_INCIDENTS_COUNT}', 'Latitude', {lat})")
    prolog.assertz(f"incidente('{ID_INCIDENTS_COUNT}', 'Longitude', {lon})")
    prolog.assertz(
        f"incidente('{ID_INCIDENTS_COUNT}', 'Incident_Station_Area', '{station_assigned[0]['StazioneAssegnata']}')")
    prolog.assertz(f"incidente('{ID_INCIDENTS_COUNT}', 'Neighbourhood', '{neigh}')")
    prolog.assertz(f"incidente('{ID_INCIDENTS_COUNT}', 'Possible_Cause', '{possile_cause}')")
    prolog.assertz(f"incidente('{ID_INCIDENTS_COUNT}', 'Property_Use', '{property_use}')")


def simulate_complete_incindent(kb, id_incident):
    df = pd.read_csv('datasets/fire_knowledgewn.csv')
    categorical = ['Area_of_Origin', 'Business_Impact', 'Extent_Of_Fire', 'Status_of_Fire_On_Arrival',
                   'Method_Of_Fire_Control', 'Ignition_Source', 'Material_First_Ignited',
                   'Smoke_Alarm_at_Fire_Origin_Alarm_Type', 'Smoke_Alarm_at_Fire_Origin_Alarm_Failure',
                   'Fire_Alarm_System_Impact_on_Evacuation', 'Fire_Alarm_System_Presence',
                   'Fire_Alarm_System_Operation']
    for attribute in categorical:
        asser = f"incidente('{id_incident}', '{attribute}', '{df[attribute].sample().values[0]}')"
        kb.assertz(asser)

    # Get the incident's TFS_Alarm_Time
    results = list(kb.query(f"incidente('{id_incident}', 'TFS_Alarm_Time', Time)"))
    tfs_alarm_time = results[0]['Time']
    tfs_arrival_time = simulate_arrival_date_incident(tfs_alarm_time, 60, 1800)
    fire_under_control_time = simulate_arrival_date_incident(tfs_arrival_time, 0, 1800)
    # Adding the remaining information
    asser = f"incidente('{id_incident}', 'TFS_Arrival_Time', '{tfs_arrival_time}')"
    kb.assertz(asser)
    asser = f"incidente('{id_incident}', 'Fire_Under_Control_Time', '{fire_under_control_time}')"
    kb.assertz(asser)
    estimated_number_person = random.randint(0, 500)
    count_of_person_rescued = random.randint(0, 500)
    civilian_casualties = random.randint(0, 30)
    kb.assertz(f"incidente('{id_incident}', 'Estimated_Number_Of_Persons_Displaced', {estimated_number_person})")
    kb.assertz(f"incidente('{id_incident}', 'Count_Of_Person_Rescued', {count_of_person_rescued})")
    kb.assertz(f"incidente('{id_incident}', 'Civilian_Casualties', {civilian_casualties})")


if __name__ == '__main__':
    kdtree = KDTreeNeighbors()
    kdtree.create_tree()

    print("Caricamento grafo...")
    G = Graph(kdtree)
    kb = KnowledgeBase()

    # kdtree.plot_graph(kdtree.neighbourhoods)

    # Loading knowledge base
    if os.path.exists(KNOWLEDGE_BASE_PATH) is False:
        print("Aggiornamento base di conoscenza...")

        kb.create_incidents_history()
        kb.create_fire_stations()
        kb.create_rules()
    else:
        print("Caricamento base di conoscenza")

    prolog = Prolog()
    prolog.consult('./knowledge_base/kb.pl')

    # Loading Estimator
    print("Caricamento stimatore...")
    estimator = Estimator()

    # Simulating avalbility of fire stations
    simulate_availability(prolog)

    close = False
    while not close:
        menu.clear()
        menu.main_menu()
        choice = input("-----> ")
        print(choice, "E ", EXIT_CHOICE)
        if choice is EXIT_CHOICE:
            close = True

        if choice == CHOICE_SIMULATE_INCIDENT:
            simulate_incident(kdtree, kb, prolog, G)
            ID_INCIDENTS_COUNT += 1
            choice = input("Premi un tasto per continuare...")
        elif choice == CHOICE_CLOSING_INCIDENT:
            complete = False
            while complete is False:
                menu.close_incident()
                id_incident = input("-----> ")
                if id_incident == '1':
                    results = list(
                        prolog.query("setof(Individuo, Proprieta^Valore^(incidente(Individuo, Proprieta, Valore), "
                                     "Proprieta \= 'TFS_Arrival_Time', \+ incidente(Individuo, 'TFS_Arrival_Time', _)), "
                                     "Incidenti)."))
                    if len(results) > 0 and 'Incidenti' in results[0] and len(results[0]['Incidenti']) > 0:
                        value = results[0]['Incidenti']
                        if isinstance(value, (list, tuple, set)):
                            for item in value:
                                menu.active_incident_info(item, prolog)
                        else:
                            print(value)
                    else:
                        print("Nessun incendio in corso...")

                if id_incident == '2':
                    print("Indicare numero incidente: ")
                    id_incident = input("-----> ")
                    if int(id_incident):
                        simulate_complete_incindent(prolog, id_incident)
                        estimated_loss = kb.estimate_dollar_loss(id_incident, prolog, estimator)
                        prolog.assertz(f"incidente('{id_incident}', 'Estimated_Dollar_Loss', {int(estimated_loss)})")
                        incident_info = kb.get_incident_info(id_incident, prolog)
                        additional_info = kb.get_additional_incident_info(id_incident, prolog)
                        menu.incident_info(id_incident, incident_info)
                        print(additional_info)
                        menu.additional_incident_info(id_incident, additional_info)
                if id_incident == '0':
                    complete = True
        elif choice == CHOICE_KNOWLEDGE_BASE:
            while choice is not EXIT_CHOICE:
                menu.clear()
                menu.knowledge_base()
                choice = input("-----> ")

                if choice == '1':
                    while choice is not EXIT_CHOICE:
                        query = input("Query -----> ")
                        if query != '0':
                            try:
                                results = list(prolog.query(query))
                                if len(results) > 0:
                                    keys = results[0].keys()
                                    if len(keys) > 0:
                                        for key in keys:
                                            print(f"{key}:")
                                            for result in results:
                                                value = result[key]
                                                if isinstance(value, (list, tuple, set)):
                                                    print("Valori:")
                                                    for item in value:
                                                        print(item)
                                                else:
                                                    print(value)
                                    else:
                                        print("Vero.")
                                else:
                                    print("Falso.")
                                    # print("No results found.")

                            except ValueError:
                                print("Execption: ", ValueError)
                                print("Errore sintattico/semantico. Riprovare.")
                        if query == '0':
                            choice = EXIT_CHOICE
        elif choice == CHOICE_PATH_FINDING:
            while choice is not EXIT_CHOICE:
                menu.search_path()
                choice = input("-----> ")
                print(choice, "E ", EXIT_CHOICE)
                if choice == '1':
                    complete = False
                    while complete is False:
                        menu.clear()
                        menu.search_neighbourhoods(G.name_to_number)
                        print("Primo quartiere (numero): ")
                        first_neigh = input("-----> ")
                        print("Secondo quartiere (numero): ")
                        second_neigh = input("-----> ")
                        path = G.dijkstra_search(int(first_neigh), int(second_neigh))
                        # G.plot_map_graph(kdtree, path)
                        G.plot_path(path)
                        complete = True
                elif choice == '2':
                    complete = False
                    while complete is False:
                        menu.clear()
                        print("Prima Stazione (numero): ")
                        first_neigh = input("-----> ")
                        print("Seconda Stazione (numero): ")
                        second_neigh = input("-----> ")
                        path = G.dijkstra_search('s' + str(first_neigh), 's' + str(second_neigh))
                        G.plot_path(path)
                        complete = True
                elif choice == '3':
                    complete = False
                    while complete is False:
                        menu.clear()
                        menu.search_neighbourhoods(G.name_to_number)
                        print("Quartiere(numero): ")
                        first_neigh = input("-----> ")
                        menu.search_stations(G.name_to_number_stations)
                        print("Seconda Stazione (numero): ")
                        second_neigh = input("-----> ")
                        path = G.dijkstra_search(int(first_neigh), 's' + str(second_neigh))
                        G.plot_path(path)
                        # G.plot_map_graph(kdtree, path)
                        complete = True
                elif choice == '4':
                    while choice is not EXIT_CHOICE:
                        menu.search_multiple_path()
                        choice = input("---> ")

                        if choice == '1':
                            man_type = f"\"Nessuna manutenzione necessaria\""
                            results = list(prolog.query(f"findall(Staz, (manutenzione_necessaria(Staz, De), "
                                                        f"De \= \"Nessuna manutenzione necessaria\"), Stazioni)"))
                            print("Stazioni che necessitano di manutenzione: ")
                            kb.print_query_results(results, knowledge_base.OUTPUT_LIST_MODE, 'Stazioni')
                        elif choice == '2':
                            print("Quartieri con maggior rischio di incendio: ")
                            results = list(prolog.query("findall(Q, quartiere_ad_alto_rischio(Q), Quartieri)"))
                            for result in results[0]['Quartieri']:
                                print(result + ", ", str(G.name_to_number[result]))
                        elif choice == '3':
                            menu.search_neighbourhoods(G.name_to_number)
                            menu.search_stations(G.name_to_number_stations)
                            print("Indica quartiere di partenza: ")
                            first_neigh = input("---> ")
                            print("Indica il numero dei quartieri e/o stazioni (es. 114, s141, 132): ")
                            list_neigh = input("---> ")
                            split_list = list_neigh.replace(" ", "").split(",")
                            result_list = [int(x) if x.isdigit() else x for x in split_list]
                            print(result_list)
                            path = G.tsp_search(int(first_neigh), result_list)
                            G.plot_path(path)
                        elif choice == '4':
                            menu.search_neighbourhoods(G.name_to_number)
                            menu.search_stations(G.name_to_number_stations)
                            print("Indica quartiere di partenza: ")
                            first_neigh = input("---> ")
                            print("Indica il numero dei quartieri e/o stazioni (es. 114, s141, 132): ")
                            list_neigh = input("---> ")
                            split_list = list_neigh.replace(" ", "").split(",")
                            result_list = [int(x) if x.isdigit() else x for x in split_list]
                            result_list.insert(0, int(first_neigh))
                            print(result_list)
                            path_tot = []
                            len_path_tot = 0
                            for i in range(len(result_list) - 1):
                                start = result_list[i]
                                end = result_list[i + 1]
                                path_temp = G.dijkstra_search(start, end)
                                len_path_temp = G.path_length(path_temp)
                                len_path_tot = len_path_tot + len_path_temp
                                path_tot.extend(path_temp[:-1])

                            path_tot.append(result_list[-1])
                            # print("Percorso totale:", path_tot)
                            # print("Lunghezza totale:", len_path_tot)
                            # G.plot_map_graph(kdtree, path_tot)
                            G.plot_path(path_tot)
        elif choice == EXIT_CHOICE:
            print("Sistema in standby...")
        else:
            print("Scelta non valida. Per favore, inserisci un numero tra 1 e 4.")
