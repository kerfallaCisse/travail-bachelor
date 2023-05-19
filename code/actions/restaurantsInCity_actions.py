from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
from SPARQLWrapper import SPARQLWrapper2

osmap_endpoint = SPARQLWrapper2("https://sophox.org/sparql") # Open street map endpoint

class RestaurantsInCity(Action):

    def name(self) -> Text:
        return "action_restaurants_city"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        city = tracker.get_slot("city")
                
        with open("data/city.txt", "r", encoding="utf-8") as f:
            lines = f.readlines()
            lines_clean = [line.strip() for line in lines]
            if city not in lines_clean:
                dispatcher.utter_message(text="Désolé nous n'avons trouvé aucun restaurant dans cette ville\n\nIl se peut que la ville mentionnée ne soit pas une ville suisse")
                return []
            else:
                restaurants = list()
                
                # amenity permet de décire des équipements utiles pour les visiteurs et résidents
                osmap_endpoint.setQuery(f"""
                                        SELECT ?osmn ?type ?loc ?name ?street ?cuisine ?hours
                                        WHERE{{
                                            VALUES ?type {{"bar" "restaurant" "pub" "cafe" "food_court" "biergarten" "fast_food"}}
                                            ?osmn osmt:addr:city "{city}";
                                                osmt:amenity ?type;
                                                osmm:loc ?loc ;
                                                osmt:name ?name ;
                                                osmt:addr:street ?street .
                                            # FILTER(lcase(str(?city))="{city}"), prend plus de temps
                                            OPTIONAL {{
                                                ?osmn osmt:cuisine ?cuisine ;
                                                osmt:opening_hours ?hours .   
                                            }}    
                                        }}
                                        """)
                results = osmap_endpoint.query().bindings
                restaurant_names = list()
                if len(results) == 0:
                    dispatcher.utter_message(text="Désolé nous n'avons trouvé aucun restaurant dans cette ville")
                    return []
                limit = 0
                for result in results:
                    if limit == 10:
                        break
                    
                    rest_name = result['name'].value
                    with open("data/rest_name.txt","a+",encoding="utf-8") as f:
                        lines = f.readlines()
                        lines_clean = [l.strip() for l in lines]
                        if rest_name not in lines_clean:
                            f.write(rest_name+"\n")
                            restaurant_names.append(rest_name)
                        
                    rest_street = result["street"].value
                    rest_loc = result["loc"].value
                    rest_slots = f"{rest_name} {rest_loc}"
                    restaurants.append(rest_slots)
                    dispatcher.utter_message(text=f"Nom du restaurant: {rest_name}\n- Adresse: {rest_street}")
                    try:
                        rest_cuisine = result["cuisine"].value
                        rest_hours = result["hours"].value
                        if rest_cuisine is not None:
                            dispatcher.utter_message(text=f"- Type de cuisine: {rest_cuisine}")
                        if rest_hours is not None:
                            dispatcher.utter_message(text=f"- Horaires: {rest_hours}")
                    except KeyError:
                        pass
                    
                    dispatcher.utter_message(text=">>>>>>>>")
                    limit += 1
                
                dispatcher.utter_message(text="Peux tu préciser ta recherche ?")

                return [SlotSet("curiosity", restaurants)]


    
    
