from prettytable import PrettyTable
from os import system, name


def clear():
    # for windows
    if name == 'nt':
        _ = system('cls')

    # for mac and linux(here, os.name is 'posix')
    else:
        _ = system('clear')


def main_menu():
    print("""████████╗    ███████╗    ███████╗
    ╚══██╔══╝    ██╔════╝    ██╔════╝
       ██║       █████╗      ███████╗
       ██║       ██╔══╝      ╚════██║
       ██║       ██║         ███████║
       ╚═╝       ╚═╝         ╚══════╝                                               
    """)
    print(f"\U0001F6A8 🅃🄾🅁🄾🄽🅃🄾 🄵🄸🅁🄴 🅂🅈🅂🅃🄴🄼 \U0001F6A8")
    menu_table = PrettyTable()
    menu_table.field_names = ["Opzione", "Descrizione"]
    menu_table.add_row(["1", "Registra nuovo incendio"])
    menu_table.add_row(["2", "Concludi incendio in corso"])
    menu_table.add_row(["3", "Consulta base di conoscenza"])
    menu_table.add_row(["4", "Ricerca percorso"])
    menu_table.add_row(["0", "Esci"])
    menu_table.align = "l"
    menu_table.junction_char = "*"
    menu_table.horizontal_char = "-"
    menu_table.vertical_char = "|"
    print(menu_table.get_string(title="\U0001F692 TORONTO FIRE SYSTEM \U0001F692", border=True))


def knowledge_base():
    menu_table = PrettyTable()
    menu_table.field_names = ["Opzione", "Descrizione"]
    menu_table.add_row(["1", "Query"])
    menu_table.add_row(["0", "Esci"])
    menu_table.align = "l"
    menu_table.junction_char = "*"
    menu_table.horizontal_char = "-"
    menu_table.vertical_char = "|"
    print(menu_table.get_string(title="\U0001F692 TORONTO FIRE SYSTEM \U0001F692", border=True))


def search_path():
    menu_table = PrettyTable()
    menu_table.field_names = ["Opzione", "Descrizione"]
    menu_table.add_row(["1", "Ricerca percorso tra quartieri"])
    menu_table.add_row(["2", "Ricerca percorso tra stazioni"])
    menu_table.add_row(["3", "Ricerca percorso tra stazione e quartiere"])
    menu_table.add_row(["4", "Pianifica percorso multiplo"])
    menu_table.add_row(["0", "Esci"])
    menu_table.align = "l"
    menu_table.junction_char = "*"
    menu_table.horizontal_char = "-"
    menu_table.vertical_char = "|"
    print(menu_table.get_string(title="\U0001F692 TORONTO FIRE SYSTEM \U0001F692", border=True))

def search_multiple_path():
    menu_table = PrettyTable()
    menu_table.field_names = ["Opzione", "Descrizione"]
    menu_table.add_row(["1", "Mostra stazioni che necessitano di manutenzione"])
    menu_table.add_row(["2", "Mostra quartieri con maggiore rischio incendio"])
    menu_table.add_row(["3", "Pianifica andata e ritorno"])
    menu_table.add_row(["4", "Pianifica percorso esatto"])
    menu_table.add_row(["0", "Esci"])
    menu_table.align = "l"
    menu_table.junction_char = "*"
    menu_table.horizontal_char = "-"
    menu_table.vertical_char = "|"
    print(menu_table.get_string(title="\U0001F692 TORONTO FIRE SYSTEM \U0001F692", border=True))

def search():
    menu_table = PrettyTable()
    menu_table.field_names = ["Opzione", "Descrizione"]
    menu_table.add_row(["1", "Ricerca percorso tra quartieri"])
    menu_table.add_row(["2", "Ricerca percorso tra stazioni"])
    menu_table.add_row(["3", "Ricerca percorso tra stazione e quartiere"])
    menu_table.add_row(["0", "Esci"])
    menu_table.align = "l"
    menu_table.junction_char = "*"
    menu_table.horizontal_char = "-"
    menu_table.vertical_char = "|"
    print(menu_table.get_string(title="TORONTO FIRE SYSTEM", border=True))


def search_stations(stations):
    print("Quartieri: \n", stations)
    n_rows = 30
    n_cols = 3
    table = PrettyTable()
    table.field_names = ["Scheda: " + str(i) for i in range(1, n_cols + 1)]
    for i in range(n_rows):
        row = []
        for j in range(n_cols):
            index = i * n_cols + j
            if index < len(stations):
                row.append(stations[index])
            else:
                row.append("")
        table.add_row(row)

    print(table)


def search_neighbourhoods(quartieri):
    # print("Quartieri: \n", quartieri)
    n_rows = 21
    n_cols = 4
    table = PrettyTable()
    table.field_names = ["Scheda " + str(i) for i in range(1, n_cols + 1)]
    for i in range(n_rows):
        row = []
        for j in range(n_cols):
            index = i * n_cols + j
            if index < len(quartieri):
                row.append(list(quartieri.keys())[index] + ": " + str(quartieri[list(quartieri.keys())[index]]))
            else:
                row.append("")
        table.add_row(row)

    table.align["Scheda 1"] = "l"
    table.align["Scheda 2"] = "l"
    table.align["Scheda 3"] = "l"
    table.align["Scheda 4"] = "l"
    print(table)


def close_incident():
    menu_table = PrettyTable()
    menu_table.field_names = ["Opzione", "Descrizione"]
    menu_table.add_row(["1", "Mostra incidenti in corso"])
    menu_table.add_row(["2", "Concludi incidente"])
    menu_table.add_row(["0", "Esci"])
    menu_table.align = "l"
    menu_table.junction_char = "*"
    menu_table.horizontal_char = "-"
    menu_table.vertical_char = "|"
    print(menu_table.get_string(title="\U0001F692 TORONTO FIRE SYSTEM \U0001F692", border=True))


def active_incident_info(id_incident, kb):
    menu_table = PrettyTable()
    menu_table.field_names = ["Caratteristica", "Descrizione"]
    menu_table.add_row(["ID Incidente: ", id_incident])
    results = list(kb.query(f"incidente('{id_incident}', 'Incident_Station_Area', Station)"))
    menu_table.add_row(["Stazione Assegnata: ", results[0]['Station']])
    results = list(kb.query(f"incidente('{id_incident}', 'Neighbourhood', Neighbour)"))
    menu_table.add_row(["Quartiere: ", results[0]['Neighbour']])
    query_lat = f"incidente('{id_incident}', 'Latitude', Lat)"
    query_lon = f"incidente('{id_incident}', 'Longitude', Lon)"
    lat = list(kb.query(query_lat))
    lon = list(kb.query(query_lon))
    menu_table.add_row(["Latitudine: ", lat[0]['Lat']])
    menu_table.add_row(["Longitudine: ", lon[0]['Lon']])
    results = list(kb.query(f"incidente('{id_incident}', 'Possible_Cause', Cause)"))
    menu_table.add_row(["Possibile Causa: ", results[0]['Cause']])
    results = list(kb.query(f"incidente('{id_incident}', 'Property_Use', Property)"))
    menu_table.add_row(["Tipo di proprietà: ", results[0]['Property']])
    results = list(kb.query(f"incidente('{id_incident}', 'TFS_Alarm_Time', AlarmTime)"))
    menu_table.add_row(["Data scatto allarme: ", results[0]['AlarmTime']])
    menu_table.align = "l"
    menu_table.junction_char = "*"
    menu_table.horizontal_char = "-"
    menu_table.vertical_char = "|"
    print(menu_table.get_string(title="\U0001F4C4  INFORMAZIONI INCIDENTE \U0001F4C4", border=True))


def incident_info(id_incident, attributes):
    menu_table = PrettyTable()
    menu_table.field_names = ["Caratteristica", "Descrizione"]
    menu_table.add_row(["ID Incidente: ", id_incident])
    menu_table.add_row(["Quartiere Incidente: ", attributes['Neighbourhood']])
    menu_table.add_row(["Stazione Assegnata: ", attributes['Incident_Station_Area']])
    menu_table.add_row(["Quartiere Stazione: ", attributes['NeighbourhoodStaz']])
    menu_table.add_row(["Latitudine: ", attributes['Latitude']])
    menu_table.add_row(["Longitudine: ", attributes['Longitude']])
    menu_table.add_row(["Possibile Causa: ", attributes['Possible_Cause']])
    menu_table.add_row(["Tipo di proprietà: ", attributes['Property_Use']])
    menu_table.add_row(["Area di origine: ", attributes['Area_of_Origin']])
    menu_table.add_row(["Sorgente di ignizione: ", attributes['Ignition_Source']])
    menu_table.add_row(["Primo material innescato: ", attributes['Material_First_Ignited']])
    menu_table.add_row(["Data scatto allarme: ", attributes['TFS_Alarm_Time']])
    menu_table.add_row(["Data di arrivo (stazione): ", attributes['TFS_Arrival_Time']])
    menu_table.add_row(["Data messa in sicurezza: ", attributes['Fire_Under_Control_Time']])
    menu_table.add_row(["Stato fuoco all'arrivo: ", attributes['Status_of_Fire_On_Arrival']])
    menu_table.add_row(["Espansione incendio: ", attributes['Extent_Of_Fire']])
    menu_table.add_row(["Stima perdita in denaro: ", (str(attributes['Estimated_Dollar_Loss']) + "$")])
    menu_table.add_row(["Impatto sul Business: ", attributes['Business_Impact']])
    menu_table.add_row(["Stima persona messe in sicurezza: ", attributes['Estimated_Number_Of_Persons_Displaced']])
    menu_table.align = "l"
    menu_table.junction_char = "*"
    menu_table.horizontal_char = "-"
    menu_table.vertical_char = "|"
    print(menu_table.get_string(title="\U0001F4C4  INFORMAZIONI INCIDENTE \U0001F4C4", border=True))

def additional_incident_info(id_incident, attributes):
    menu_table = PrettyTable()
    menu_table.field_names = ["Caratteristica", "Descrizione"]
    menu_table.add_row(["Danno Impatto economico:", attributes['EconomyImpact']])
    menu_table.add_row(["Potenzialmente pericoloso:", attributes['PotentialRisk']])
    menu_table.add_row(["Rischio inquinamento elevato: ", attributes['PollutionRisk']])
    menu_table.add_row(["Rischio danni strutturali: ", attributes['PropertyRisk']])
    menu_table.align = "l"
    menu_table.junction_char = "*"
    menu_table.horizontal_char = "-"
    menu_table.vertical_char = "|"
    print(menu_table.get_string(title="\U0001F4C4  INFORMAZIONI INCIDENTE \U0001F4C4", border=True))