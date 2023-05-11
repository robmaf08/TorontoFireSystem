import pandas as pd
import numpy as np

OUTPUT_LIST_MODE = 'List'
OUTPUT_ONCE_MODE = 'Once'


class KnowledgeBase:
    def create_incidents_history(self):
        # Reading fire incidents dataset
        df = pd.read_csv('datasets/fire_knowledgewn.csv')

        attributes_with_string = ["Area_of_Origin", "Business_Impact", "Extent_Of_Fire",
                                  "Fire_Alarm_System_Impact_on_Evacuation",
                                  "Fire_Alarm_System_Operation", "Fire_Alarm_System_Presence",
                                  "Ignition_Source",
                                  "Material_First_Ignited", "Method_Of_Fire_Control", "Possible_Cause", "Property_Use",
                                  "Smoke_Alarm_at_Fire_Origin_Alarm_Failure", "Smoke_Alarm_at_Fire_Origin_Alarm_Type",
                                  "Status_of_Fire_On_Arrival",
                                  "TFS_Alarm_Time", "TFS_Arrival_Time",
                                  "Fire_Under_Control_Time", "Last_TFS_Unit_Clear_Time", 'Incident_Station_Area',
                                  'Neighbourhood']

        attributes_numerical = ["Civilian_Casualties", "Count_of_Persons_Rescued",
                                "Estimated_Dollar_Loss", "Estimated_Number_Of_Persons_Displaced",
                                "Latitude", "Longitude"]

        count = 0
        with open("./knowledge_base/kb.pl", "a") as kb:
            # Defining facts
            kb.writelines("% Definizione dei fatti \n\n")
            for index, row in df.iterrows():
                ind = count

                for attribute in attributes_with_string:
                    prop = attribute
                    val = row[attribute]
                    prop_string = f"incidente('{ind}', '{prop}', '{val}').\n"
                    kb.writelines(prop_string)

                for attribute in attributes_numerical:
                    prop = attribute
                    val = row[attribute]
                    prop_string = f"incidente('{ind}', '{prop}', {val}).\n"
                    kb.writelines(prop_string)

                count += 1

            kb.writelines("% --------------------------- \n\n")

    def create_fire_stations(self):
        # Reading fire stations dataset
        fire_stations = pd.read_csv('datasets/fire-station-locations_wn.csv')

        with open("./knowledge_base/kb.pl", "a") as kb:
            kb.writelines("% Definizione dei fatti stazioni vigili del fuoco \n\n")
            for index, row in fire_stations.iterrows():
                prop_string_lon = f"stazione('{row['STATION']}', 'Longitude', {row['Longitude']}).\n"
                prop_string_lan = f"stazione('{row['STATION']}', 'Latitude', {row['Latitude']}).\n"
                prop_string_year = f"stazione('{row['STATION']}', 'YEAR_BUILD', {row['YEAR_BUILD']}).\n"
                prop_string_neigh = f"stazione('{row['STATION']}', 'Neighbourhood', '{row['Neighbourhood']}').\n"
                kb.writelines(prop_string_lon)
                kb.writelines(prop_string_lan)
                kb.writelines(prop_string_year)
                kb.writelines(prop_string_neigh)
                prop_string_disp = f"stazione('{row['STATION']}', 'Disponibilita', 1).\n"
                prop_string_state = f"stazione('{row['STATION']}', 'StatoApertura', 1).\n"
                kb.writelines(prop_string_disp)
                kb.writelines(prop_string_state)

            kb.writelines("% --------------------------- \n\n")

    def create_rules(self):
        # Writing prolog rules
        with open("./knowledge_base/rules.txt", "r") as rules_file, open("./knowledge_base/kb.pl", "a") as kb_file:
            for rule in rules_file:
                kb_file.write(rule)

        # Writing clustering results
        with open("./clustering/clustering_results.txt", "r") as rules_file, open("./knowledge_base/kb.pl", "a") as kb_file:
            for rule in rules_file:
                kb_file.write(rule)

    def station_avaiability(self, prolog, avaiable):
        if avaiable is True:
            results = list(
                prolog.query("{Stazioni}/(findall(Stazione, stazione(Stazione, 'Disponibilita', 1), Stazioni))"))
            print("Stazioni Disponibili: ")
        else:
            results = list(
                prolog.query("{Stazioni}/(findall(Stazione, stazione(Stazione, 'Disponibilita', 0), Stazioni))"))
            print("Stazioni Non Disponibili: ")
        self.print_query_results(results, OUTPUT_LIST_MODE, 'Stazioni')

    def estimate_dollar_loss(self, id_incident, prolog, estimator):
        incident_info = self.get_incident_info(int(id_incident), prolog)
        # Columns that need to be encoded
        cols = ['Area_of_Origin', 'Business_Impact', 'Extent_Of_Fire',
                'Fire_Alarm_System_Impact_on_Evacuation',
                'Fire_Alarm_System_Operation', 'Fire_Alarm_System_Presence',
                'Ignition_Source', 'Material_First_Ignited',
                'Method_Of_Fire_Control', 'Possible_Cause', 'Property_Use',
                'Smoke_Alarm_at_Fire_Origin_Alarm_Failure',
                'Smoke_Alarm_at_Fire_Origin_Alarm_Type',
                'Status_of_Fire_On_Arrival']
        # Create a empty DataFrame with the same columns of the original one
        empty_df = pd.DataFrame(np.nan, index=[0], columns=estimator.df.columns)
        # Insert missing values with incident information
        empty_df.loc[:, incident_info.keys()] = pd.DataFrame(incident_info, index=[0])
        # Fit ordinal encoder and return encoded label
        empty_df[cols] = estimator.ordinal_encoder.transform(empty_df[cols])
        columns_to_drop = ['Fire_Under_Control_Time',
                           'Fire_Alarm_System_Impact_on_Evacuation', 'Estimated_Dollar_Loss',
                           'Possible_Cause', 'Method_Of_Fire_Control', 'Civilian_Casualties',
                           'Count_of_Persons_Rescued', 'Fire_Alarm_System_Impact_on_Evacuation',
                           'Smoke_Alarm_at_Fire_Origin_Alarm_Type',
                           'Ext_agent_app_or_defer_time', 'TFS_Alarm_Time', 'TFS_Arrival_Time',
                           'Last_TFS_Unit_Clear_Time', 'Unnamed: 0', 'Incident_Ward',
                           'Neighbourhood', 'NeighbourhoodStaz']
        empty_df2 = empty_df.drop(columns=columns_to_drop)
        X_test = empty_df2.to_numpy()
        print("Possibile perdita in denaro: ")
        estimated_loss = estimator.predict_value(X_test)
        return estimated_loss

    # Methods for incidents info
    def get_incident_info(self, id_incident, prolog):
        # Defining dictionary for incident info
        incident_info = {}

        attributes = ['Area_of_Origin', 'Business_Impact', 'Civilian_Casualties', 'Count_of_Persons_Rescued',
                      'Estimated_Dollar_Loss', 'Estimated_Number_Of_Persons_Displaced',
                      'Ext_agent_app_or_defer_time', 'Extent_Of_Fire',
                      'Fire_Alarm_System_Impact_on_Evacuation', 'Fire_Alarm_System_Operation',
                      'Fire_Alarm_System_Presence', 'Fire_Under_Control_Time', 'Ignition_Source',
                      'Incident_Station_Area', 'Incident_Ward', 'Last_TFS_Unit_Clear_Time',
                      'Material_First_Ignited', 'Method_Of_Fire_Control',
                      'Possible_Cause', 'Property_Use',
                      'Smoke_Alarm_at_Fire_Origin_Alarm_Failure',
                      'Smoke_Alarm_at_Fire_Origin_Alarm_Type',
                      'Status_of_Fire_On_Arrival', 'TFS_Alarm_Time', 'TFS_Arrival_Time', 'Neighbourhood']

        for attribute in attributes:
            query = f"incidente('{id_incident}', '{attribute}', Valore)"
            result = list(prolog.query(query))
            value = result[0]['Valore'] if len(result) > 0 else None
            incident_info[attribute] = value

        # Adding float values
        query_lat = f"incidente('{id_incident}', 'Latitude', Lat)"
        query_lon = f"incidente('{id_incident}', 'Longitude', Lon)"
        query_sta = f"stazione('{incident_info['Incident_Station_Area']}', 'Neighbourhood', NeighbourhoodStaz)"
        lat = list(prolog.query(query_lat))
        lon = list(prolog.query(query_lon))
        staz = list(prolog.query(query_sta))
        incident_info['Latitude'] = float(lat[0]['Lat'])
        incident_info['Longitude'] = float(lon[0]['Lon'])
        incident_info['NeighbourhoodStaz'] = staz[0]['NeighbourhoodStaz']
        print("KB_LAT: ", incident_info['Latitude'])
        print("KB_LON: ", incident_info['Longitude'])

        return incident_info

    def get_additional_incident_info(self, id_incident, prolog):
        info = {}
        boolean_queries = [f"incidente_potenzialmente_pericoloso('{id_incident}')",
                           f"rischio_inquinamento_elevato('{id_incident}')",
                           f"rischio_danni_strutturali_elevato('{id_incident}')"]
        boolean_attributes = ['PotentialRisk', 'PollutionRisk', 'PropertyRisk']

        print(boolean_attributes[0])
        index = 0
        for query in boolean_queries:
            results = list(prolog.query(query))
            if len(results) == 0:
                info[boolean_attributes[index]] = 'No'
            else:
                info[boolean_attributes[index]] = 'Si'

            index = index + 1

        query_economic_damage = f"danno_economico('{id_incident}', Classe)"
        results = list(prolog.query(query_economic_damage))
        info['EconomyImpact'] = results[0]['Classe']
        return info

    def print_query_results(self, results, output_mode, key=None):
        if len(results) > 0:
            # Checking if specified key exist
            if key and key not in results[0]:
                print(f"Chiave '{key}' non trovata.")
                return

            # Print results for each key or specific
            keys = [key] if key else results[0].keys()
            for k in keys:
                # print(f"Results for {k}:")
                for result in results:
                    value = result[k]
                    # Check if the value is a list (or other type of iterable)
                    if isinstance(value, (list, tuple, set)):
                        # print("List of values:")
                        list_res = []

                        for item in value:
                            list_res.append(str(item))

                        if output_mode == OUTPUT_ONCE_MODE:
                            for item in list_res:
                                print(item)
                        elif output_mode == OUTPUT_LIST_MODE:
                            # print(list_res)
                            self.print_list_results(list_res)
                    else:
                        print(value)
        else:
            print(results[0].keys())
            if results[0].keys() == 0:
                print("Nessun risultato trovato.")

        return list_res

    def print_list_results(self, list_res):
        chunk_size = 7
        chunks = [list_res[i:i + chunk_size] for i in range(0, len(list_res), chunk_size)]
        for chunk in chunks:
            print(chunk)
