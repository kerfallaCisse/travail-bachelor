from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
from SPARQLWrapper import SPARQLWrapper2, POST
import requests

osmap_endpoint = SPARQLWrapper2(
    "https://sophox.org/sparql")  # Open street map endpoint

# local_endpoint_update = SPARQLWrapper2("http://localhost:7200/repositories/POC-1/rdf-graphs/service?graph=http://travail_bachelor.ch/")
# http://localhost:7200/repositories/POC-1/rdf-graphs/service?graph=http%3A%2F%2Ftravail_bachelor.ch%2F
# local_endpoint_update = SPARQLWrapper2("http://localhost:7200/repositories/POC-1/rdf-graphs/service?graph=http%3A%2F%2Ftravail_bachelor.ch%2F")
# #local_endpoint_update.addParameter("graph","http://travail_bachelor.ch/")
# local_endpoint_update.setMethod(POST)
# local_endpoint_update.setQuery(f"""
#                                PREFIX ns0: <http://www.geonames.org/ontology#>
#                                INSERT DATA {{
#                                    <https://www.openstreetmap.org/node/8818883495> a <https://www.openstreetmap.org/node/>;
#                                    ns0:name "Johnny the Ripper";
#                                    ns0:parentCountry <https://sws.geonames.org/2658434/> .
#                                }}
#                                """)
# local_endpoint_update.query()
resp = requests.post(url="http://localhost:7200/repositories/POC-1/rdf-graphs/service?default",
              data=f"<https://www.openstreetmap.org/node/8818883495> a <https://www.openstreetmap.org/node/>; ns0:name 'Johnny the Ripper'; ns0:parentCountry <https://sws.geonames.org/2658434/> .",
              headers={"Content-Type":"text/turtle"})
print(resp.status_code)
print(resp.url)
print(resp.content)
print(resp.text)
print(resp.raw)
print(resp.headers)


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
                dispatcher.utter_message(
                    text="Désolé nous n'avons trouvé aucun restaurant dans cette ville\n\nIl se peut que la ville mentionnée ne soit pas une ville suisse")
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
                    dispatcher.utter_message(
                        text="Désolé nous n'avons trouvé aucun restaurant dans cette ville")
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
                    dispatcher.utter_message(
                        text=f"Nom du restaurant: {rest_name}\n- Adresse: {rest_street}")
                    try:
                        rest_cuisine = result["cuisine"].value
                        rest_hours = result["hours"].value
                        if rest_cuisine is not None:
                            dispatcher.utter_message(
                                text=f"- Type de cuisine: {rest_cuisine}")
                        if rest_hours is not None:
                            dispatcher.utter_message(
                                text=f"- Horaires: {rest_hours}")
                    except KeyError:
                        pass

                    with open("data/rest_name.txt", "a+", encoding="utf-8") as f:
                        lines = f.readlines()
                        lines_clean = [l.strip() for l in lines]
                        if rest_name not in lines_clean:
                            restaurant_names.append(rest_name)
                            # on insère le restaurant dans le fichier texte, pour faciliter l'extraction des entités
                            f.write(rest_name+"\n")
                            # On crée un triplet avec le nom du restaurant, puis on l'insère dans le graphe
                            # local_endpoint_update.setQuery(f"""
                            #                         PREFIX ns0: <http://www.geonames.org/ontology#>
                            #                         INSERT DATA {{
                            #                             GRAPH <http://travail_bachelor.ch/> {{
                            #                                 <{osmn}> a <https://www.openstreetmap.org/node/>;
                            #                                 ns0:name "{rest_name}";
                            #                                 ns0:parentCountry <https://sws.geonames.org/2658434/> .
                            #                             }}
                            #                         }}
                            #                         """)
                            # #local_endpoint_update.setRequestMethod("POST")
                            # local_endpoint_update.method = "POST"
                            # local_endpoint_update.query()
                            # #print(local_endpoint.query().bindings)

                            # resp = requests.post(url="http://localhost:7200/repositories/POC-1/rdf-graphs/service?graph=http%3A%2F%2Ftravail_bachelor.ch%2F",
                            #               data=f"<{osmn}> a <https://www.openstreetmap.org/node/>; ns0:name '{rest_name}' ns0:parentCountry <https://sws.geonames.org/2658434/>.",
                            #               headers={"Content-Type":"text/turtle"})
                            # print(resp.status_code)

                    dispatcher.utter_message(text=">>>>>>>>")
                    limit += 1

                dispatcher.utter_message(
                    text="Peux tu préciser ta recherche ?")

                return [SlotSet("curiosity", restaurants)]
