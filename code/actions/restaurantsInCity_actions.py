from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
from SPARQLWrapper import SPARQLWrapper2
import requests
from rdflib import Literal, Namespace, URIRef, Graph
from rdflib.namespace import RDF, GEO

osmap_endpoint = SPARQLWrapper2(
    "https://sophox.org/sparql")  # Open street map endpoint
osmap_endpoint.setTimeout(60)  # query time out for the endpoint in seconde
GRAPH = Graph()


class RestaurantsInCity(Action):

    def name(self) -> Text:
        return "action_restaurants_city"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        city = tracker.get_slot("city")
        limit_query = tracker.get_slot("query_limit")
        limit = int(limit_query)

        if limit > 20:
            dispatcher.utter_message(
                response="utter_limit")
            return []

        cities = process_file("data/city.txt")  # pour la liste des villes
        # pour la liste des restaurants
        rest_names = process_file("data/rest_name.txt")

        if city not in cities:
            dispatcher.utter_message(
                text="Désolé nous n'avons trouvé aucun restaurant dans cette ville\n\nIl se peut que la ville mentionnée ne soit pas une ville suisse")
            return []

        restaurants = list()
        restaurants_mention_list = list()

        try:
            osmap_endpoint.setQuery(f"""
                                    SELECT ?osmn ?type ?loc ?longitude ?latitude ?name ?street ?postcode ?cuisine ?hours
                                    WHERE {{
                                        VALUES ?type {{"bar" "restaurant" "pub" "cafe" "food_court" "biergarten" "fast_food"}}
                                        ?osmn osmt:addr:city "{city}";
                                            osmt:amenity ?type ;
                                            osmm:loc ?loc ;
                                            osmt:name ?name ;
                                            osmt:addr:street ?street .
                                            BIND(geof:longitude(?loc) as ?longitude)
                                            BIND(geof:latitude(?loc) as ?latitude)
                                        OPTIONAL {{
                                            ?osmn osmt:cuisine ?cuisine .
                                        }}
                                        OPTIONAL {{
                                            ?osmn osmt:opening_hours ?hours . 
                                        }}
                                        OPTIONAL{{
                                            ?osmn osmt:addr:postcode ?postcode .
                                        }}    
                                    }} limit {limit_query}
                                    """)
            results = osmap_endpoint.query().bindings
            if len(results) == 0:
                dispatcher.utter_message(
                    text="Désolé nous n'avons trouvé aucun restaurant dans cette ville")
                return []
            l = 0
            for result in results:
                if l == limit:
                    break

                rest_name = result['name'].value
                osmn = result["osmn"].value
                rest_street = result["street"].value
                rest_loc = result["loc"].value
                rest_lat = result["latitude"].value
                rest_long = result["longitude"].value
                rest_slots = f"{rest_name} {rest_loc}"
                restaurants.append(rest_slots)
                restaurants_mention_list.append(rest_name)
                all_cuisines = list()
                cuisine = ""
                opening_hours = ""
                postcode = ""
                triples = f"""<{osmn}> a <https://www.openstreetmap.org/node/> ; geo1:lat "{rest_lat}" ; geo1:long "{rest_long}" ; r:adresse "{rest_street}" ;"""
                resp = str(l+1)
                dispatcher.utter_message(
                    text=f"{resp}- Nom du restaurant: {rest_name}\n- Rue: {rest_street}")
                # On récupère les valeurs optionnelles
                try:
                    cuisine = result["cuisine"].value
                    opening_hours = result["hours"].value
                    postcode = result["postcode"].value
                    if len(cuisine) != 0:
                        if cuisine.find(";") > -1:
                            all_cuisines = cuisine.split(";")
                            for c in all_cuisines:
                                triples += f"""r:cuisine "{c}" ;"""
                        else:
                            triples += f"""r:cuisine "{cuisine}" ;"""
                        dispatcher.utter_message(
                            text=f"- Type de cuisine: {cuisine}")
                    if len(opening_hours) != 0:
                        triples += f"""r:opening_hours "{opening_hours}" ;"""
                        dispatcher.utter_message(
                            text=f"- Horaires d'ouvertures: {opening_hours}")
                    if len(postcode) != 0:
                        triples += f"""r:postcode "{postcode}" ;"""
                        dispatcher.utter_message(
                            text=f"- Code postal: {postcode}")
                except KeyError:
                    pass

                if rest_name not in rest_names:
                    with open("data/rest_name.txt", "a", encoding="utf-8") as f:
                        # on insère le restaurant dans le fichier pour faciliter l'extraction des entités
                        f.write(rest_name+"\n")
                        # On insère le restaurant dans le graphe de connaissance (graphe par défaut)
                        triples += f"""ns0:name "{rest_name}"; ns0:parentCountry <https://sws.geonames.org/2658434/> ."""
                        ret = requests.post(url="http://localhost:7200/repositories/POC-1/rdf-graphs/service?default",
                                            data=triples,
                                            headers={"Content-Type": "text/turtle"})
                        # print(rest_name,ret.status_code)
                        # print(ret.content)
                        # print(ret.raw)

                        OSMPNODE = URIRef(
                            "https://www.openstreetmap.org/node/")
                        OSMPOBJECT = URIRef(osmn)
                        PARENTCOUNTRY = URIRef(
                            "https://sws.geonames.org/2658434/")
                        NS0 = Namespace("http://www.geonames.org/ontology#")
                        GEO1 = Namespace(
                            "http://www.w3.org/2003/01/geo/wgs84_pos#")
                        R = Namespace("http://restaurant#")
                        GRAPH.bind("ns0", NS0)
                        GRAPH.bind("geo", GEO)
                        GRAPH.bind("r", R)
                        cuisine_type = R.cuisine
                        openingHours = R.opening_hours
                        post_code = R.postcode
                        adresse = R.adresse
                        latitude = GEO1.lat
                        longitude = GEO1.long
                        name = NS0.name
                        parent_country = NS0.parentCountry

                        GRAPH.add((OSMPOBJECT, RDF.type, OSMPNODE))
                        GRAPH.add((OSMPOBJECT, name, Literal(rest_name)))
                        GRAPH.add((OSMPOBJECT, parent_country, PARENTCOUNTRY))

                        # On ajoute les triplets dans le fichier turtle avec la même logique
                        if cuisine.find(";") > -1:
                            all_cuisines = cuisine.split(";")
                            for c in all_cuisines:
                                GRAPH.add(
                                    (OSMPOBJECT, cuisine_type, Literal(c)))
                        else:
                            if len(cuisine) != 0:
                                GRAPH.add(
                                    (OSMPOBJECT, cuisine_type, Literal(cuisine)))
                        if len(opening_hours) != 0:
                            GRAPH.add((OSMPOBJECT, openingHours,
                                      Literal(opening_hours)))
                        if len(postcode) != 0:
                            GRAPH.add(
                                (OSMPOBJECT, post_code, Literal(postcode)))
                        GRAPH.add((OSMPOBJECT, latitude, Literal(rest_lat)))
                        GRAPH.add((OSMPOBJECT, longitude, Literal(rest_long)))
                        GRAPH.add((OSMPOBJECT, adresse, Literal(rest_street)))
                        GRAPH.parse(source="restInswitzerland.ttl")
                        GRAPH.serialize(
                            destination="restInswitzerland.ttl", format="ttl")

                dispatcher.utter_message(text=">>>>>>>>")
                l += 1
        except TimeoutError:
            dispatcher.utter_message(
                text="Désolé, la requête prend plus de temps que prévu. Reposez votre question.")
            return []

        dispatcher.utter_message(
            text="Peux-tu préciser ta recherche ? Voir la documentation pour les types de questions")
        return [SlotSet("curiosity", restaurants), SlotSet("mention_list", restaurants_mention_list)]


def process_file(file_path: str) -> list():
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
        return [l.strip() for l in lines]
