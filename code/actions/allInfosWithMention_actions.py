from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
from SPARQLWrapper import SPARQLWrapper2
import sys
from functions.resolve_mention import mapping
from functions.graph import getGraph
from rdflib import Graph
from rdflib.plugins.sparql import prepareQuery
import json
sys.path.insert(0, "/code/functions")

g = getGraph()
sparql_dbpedia = SPARQLWrapper2(
    "https://dbpedia.org/sparql")  # DBpedia endpoint
local_endpoint = SPARQLWrapper2(
    "http://localhost:7200/repositories/POC-1")  # my local graphDB endpoint


class ListerRestaurants(Action):

    def name(self) -> Text:
        return "action_lister_restaurants"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        limitation = tracker.get_slot("query_limit")
        print(limitation)

        query = prepareQuery("""
                             prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> 
                             prefix ns0: <http://www.geonames.org/ontology#> 
                             prefix geo: <http://www.w3.org/2003/01/geo/wgs84_pos#> 
                             prefix dbpedia: <http://dbpedia.org/resource/> 
                             SELECT distinct ?rn
                             WHERE {
                                ?r ns0:name ?rn
                             } limit 10
                             """)

        resp = g.query(query)
        resp_js = json.loads(resp.serialize(format="json").decode("utf-8"))
        restaurants = list()
        for result in resp_js['results']['bindings']:
            for _, v in result.items():
                restaurants.append(v['value'])

        response_to_return = ""

        for i in range(len(restaurants)):
            response_to_return += str(i+1) + "- " + restaurants[i] + "\n\n"

        response_to_return += "..\n\ntu peux spécifier ta recherche, car il y a beaucoup de restaurants"
        dispatcher.utter_message(text=response_to_return)

        return [SlotSet("mention_list", restaurants)]


class ResolveMention(Action):

    def name(self) -> Text:
        return "action_resolve_mention"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        mention_list = list()
        try:
            mention_list = tracker.get_slot('mention_list')
            if mention_list == None:
                return []
        except Exception:
            return []

        mention_list = tracker.get_slot('mention_list')
        if len(mention_list) == 0:
            return []
        mention = tracker.get_slot('mention')
        index = mapping(mention)
        restaurant = mention_list[index]

        local_endpoint.setQuery(f"""
                        prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                        prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                        prefix ns0: <http://www.geonames.org/ontology#>
                        prefix geo: <http://www.w3.org/2003/01/geo/wgs84_pos#>
                        prefix dbpedia: <http://dbpedia.org/resource/>
                        SELECT ?p ?o
                        WHERE {{
                            ?r ns0:name "{restaurant}" .
                            ?r ?p ?o .
                            FILTER (?p != rdfs:isDefinedBy && ?p != ns0:featureClass && ?p != ns0:featureCode && ?p != ns0:countryCode && ?p != ns0:parentCountry && ?p != ns0:name && ?p != rdf:type)
                        }}
                        """)

        lat = ""
        long = ""
        more_infos = ""
        location_map = ""
        locationMap_nearby_place = list()
        dbpedia = ""
        nearBy_placeList = list()
        # pour stocker les endroits proche d'un restaurant et la ressource vers la carte pour le lieu correspondant
        nearBy_placeAndMap = ""

        response = local_endpoint.query().bindings
        if len(response) == 0:
            dispatcher.utter_message(
                text="Désolé nous n'avons aucune information concernant ce restaurant")

        else:
            for result in response:
                value_object = result['o'].value
                if value_object.find("dbpedia") != -1:
                    dbpedia = value_object
                    # On récupère quelques informations concernant le restaurant
                    sparql_dbpedia.setQuery(f"""
                                            select ?abstract
                                            where {{
                                                <{dbpedia}> dbo:abstract ?abstract .
                                                FILTER(lang(?abstract)="en") 
                                            }}
                                            """)

                    resp = sparql_dbpedia.query().bindings
                    if len(resp) != 0:
                        for r in resp:
                            more_infos += r['abstract'].value + " (Anglais)."
                else:
                    value_object = value_object.lower()

                value_predicate = (result['p'].value).lower()

                if value_predicate.find("lat") != -1:
                    lat = value_object + "°N"

                if value_predicate.find("long") != -1:
                    long = value_object + "°E"

                if value_predicate.find("locationmap") != -1:
                    location_map = value_object

                if value_predicate.find("nearby") != -1:
                    nearBy_rdf = value_object
                    # On parse le graph et on le parcours
                    g_nearby = Graph().parse(nearBy_rdf)

                    q = """
                            prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                            prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                            prefix ns0: <http://www.geonames.org/ontology#>
                            SELECT ?s ?p ?o
                            WHERE {
                                ?s rdf:type ns0:Feature .
                                ?s ?p ?o
                            }
                    """
                    resp = g_nearby.query(q)
                    resp_js = json.loads(resp.serialize(
                        format="json").decode("utf-8"))

                    for result in resp_js['results']['bindings']:
                        for k, v in result.items():
                            if k == "s":
                                placeMap = v['value']
                                if placeMap not in locationMap_nearby_place:
                                    locationMap_nearby_place.append(placeMap)

                            if k == "o" and v['type'] == "literal":
                                # On récupère le nom des endroits qui sont proche du restaurant. Attention, ces endroits ne sont pas des restaurant
                                # Ils font partie d'une autre classe
                                nearby_place_name = v['value']
                                if nearby_place_name not in nearBy_placeList:
                                    nearBy_placeList.append(nearby_place_name)

            # Les deux listes auront toujours la même taille, car les données sont récupérés du résultats de la requête précédente
            for i in range(len(nearBy_placeList)):
                nearBy_placeAndMap += "- " + \
                    nearBy_placeList[i] + "--> " + \
                    locationMap_nearby_place[i] + "\n"

            # On vérifie qu'on possède les données
            if len(more_infos) != 0:
                dispatcher.utter_message(text=more_infos)
            if len(lat) != 0 and len(long) != 0:
                text = f"""Sa latitude est de {lat} et sa longitude est de {long}."""
                dispatcher.utter_message(text=text)
            if len(location_map) != 0:
                dispatcher.utter_message(
                    text=f"Visualisation du restaurant {restaurant} sur une carte: {location_map}")
            if len(nearBy_placeAndMap) != 0:
                dispatcher.utter_message(
                    text=f"Le restaurant {restaurant} est proche des lieux suivants:\n\n{nearBy_placeAndMap}")

        return []

class RestaurantsSlotLimitation(Action):
    def name(self) -> Text:
        return "action_restaurants_limitation"
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(
            text="Combien de restaurant souhaitez vous lister (mentionnez un nombre) ?")
        return [SlotSet("rest_ville", False)]

