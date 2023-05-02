from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
from SPARQLWrapper import SPARQLWrapper2
import sys
from functions.resolve_place import resolve_place
from functions.graph import getGraph
from rdflib import Graph
from .allInfosWithMention_actions import local_endpoint, sparql_dbpedia
from rdflib.plugins.sparql import prepareQuery
sys.path.insert(0, "/code/functions")

# sparql_dbpedia = SPARQLWrapper2(
#     "https://dbpedia.org/sparql")  # DBpedia endpoint
# local_endpoint = SPARQLWrapper2(
#     "http://localhost:7200/repositories/POC-1")  # my local graphDB endpoint


class RestaurantsInCity(Action):

    def name(self) -> Text:
        return "action_restaurants_endroit"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        place = tracker.get_slot("place").lower()
    
        place = resolve_place(place)
        if place == "no key":
            dispatcher.utter_message(text="Désolé nous n'avons trouvé aucun restaurant dans cet endroit")
            return []

        # On parcours les restaurants dans un endroit #
        local_endpoint.setQuery("""
                             PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                             SELECT ?dbpedia
                             WHERE {
                                 ?r rdfs:seeAlso ?dbpedia
                             }
                             """)
        response = local_endpoint.query().bindings
        all_restaurants_dbpedia = list()
        for r in response:
            ressource = r['dbpedia'].value
            if ressource.find("dbpedia") != -1 and ressource not in all_restaurants_dbpedia:
                all_restaurants_dbpedia.append(ressource)
        
        restaurantsIn_place = set()
        
        for rest in all_restaurants_dbpedia:
            sparql_dbpedia.setQuery(f"""
                                    SELECT ?rn 
                                    WHERE {{
                                        <{rest}> dbo:abstract ?abs .
                                        FILTER(lang(?abs)="en") .
                                        FILTER CONTAINS(lcase(str(?abs)), "{place}")
                                        # on récupère éventuellement le nom du restaurant
                                        <{rest}> rdfs:label ?rn .
                                        FILTER(lang(?rn)="en")
                                    }}
                                    """)
        
            resp_js = sparql_dbpedia.query().bindings    
            if len(resp_js) != 0:
                #### Alors dans ce cas, c'est un restaurant qui se trouve dans cet endroit ####
                for r in resp_js:
                    rn = r['rn'].value
                    restaurantsIn_place.add(rn)
        
        response_to_return = ""
        restaurants_place = list(restaurantsIn_place)
        for i in range(len(restaurants_place)):
            response_to_return += str(i+1) + "- " + restaurants_place[i] + "\n\n"
        dispatcher.utter_message(text=response_to_return)

        return [SlotSet("mention_list", restaurants_place)]
