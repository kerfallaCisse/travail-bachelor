from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
from SPARQLWrapper import SPARQLWrapper2
import requests

osmap_endpoint = SPARQLWrapper2(
    "https://sophox.org/sparql")  # Open street map endpoint

class RestaurantsInCity(Action):

    def name(self) -> Text:
        return "action_restaurants_city"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        city = tracker.get_slot("city")
        cities = process_file("data/city.txt") # pour la liste des villes
        rest_names = process_file("data/rest_name.txt") # pour la liste des restaurants
        
        if city not in cities:
            dispatcher.utter_message(text="Désolé nous n'avons trouvé aucun restaurant dans cette ville\n\nIl se peut que la ville mentionnée ne soit pas une ville suisse")
            return []
        
        restaurants = list()
        osmap_endpoint.setQuery(f"""
                                SELECT ?osmn ?type ?loc ?name ?street ?cuisine ?hours
                                WHERE {{
                                    VALUES ?type {{"bar" "restaurant" "pub" "cafe" "food_court" "biergarten" "fast_food"}}
                                    ?osmn osmt:addr:city "{city}";
                                        osmt:amenity ?type ;
                                        osmm:loc ?loc ;
                                        osmt:name ?name ;
                                        osmt:addr:street ?street .
                                    OPTIONAL {{
                                        ?osmn osmt:cuisine ?cuisine ;
                                              osmt:opening_hours ?hours . 
                                    }}    
                                }}
                                """)
        results = osmap_endpoint.query().bindings
        if len(results) == 0:
            dispatcher.utter_message(text="Désolé nous n'avons trouvé aucun restaurant dans cette ville")
            return []
        limit = 0
        for result in results:
            if limit == 10:
                break
            
            rest_name = result['name'].value
            osmn = result["osmn"].value
            rest_street = result["street"].value
            rest_loc = result["loc"].value
            rest_slots = f"{rest_name} {rest_loc}"
            restaurants.append(rest_slots)
            dispatcher.utter_message(text=f"- Nom du restaurant: {rest_name}\n- Adresse: {rest_street}")  
            # On récupère les valeurs optionnelles
            try:
                cuisine = result["cuisine"].value
                opening_hours = result["hours"].value
                dispatcher.utter_message(text=f"- Type de cuisine: {cuisine}\n- Horaires d'ouverture: {opening_hours}")
            except KeyError:
                pass   
            
            if rest_name not in rest_names:
                with open("data/rest_name.txt","a",encoding="utf-8") as f: 
                    f.write(rest_name+"\n") # on insère le restaurant dans le fichier pour faciliter l'extraction des entités
                    # On insère le restaurant dans le graphe de connaissance (graphe par défaut)
                    requests.post(url="http://localhost:7200/repositories/POC-1/rdf-graphs/service?default",
                                    data=f"<{osmn}> a <https://www.openstreetmap.org/node/>; ns0:name '{rest_name}'; ns0:parentCountry <https://sws.geonames.org/2658434/> .",
                                    headers={"Content-Type":"text/turtle"})
            dispatcher.utter_message(text=">>>>>>>>")        
            limit += 1
        
        dispatcher.utter_message(text="Peux-tu préciser ta recherche ? Voir la documentation pour les types de questions")
        return [SlotSet("curiosity", restaurants)]

def process_file(file_path: str) -> list():
    with open(file_path,"r",encoding="utf-8") as f:
        lines = f.readlines()
        return [l.strip() for l in lines]