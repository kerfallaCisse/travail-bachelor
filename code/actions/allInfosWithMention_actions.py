from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
from SPARQLWrapper import SPARQLWrapper2
import sys
from functions.resolve_mention import mapping
from functions.rest_infos import getRestInfos

sys.path.insert(0, "/code/functions")

sparql_dbpedia = SPARQLWrapper2(
    "https://dbpedia.org/sparql")  # DBpedia endpoint
local_endpoint = SPARQLWrapper2(
    "http://graphdb-server:7200/repositories/POC-1")  # my local graphDB endpoint


class ListerRestaurants(Action):

    def name(self) -> Text:
        return "action_lister_restaurants"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        limit_query = tracker.get_slot("query_limit")
        if int(limit_query) > 20:
            dispatcher.utter_message(response="utter_limit")
            return []

        local_endpoint.setQuery(f"""
                                prefix ns0: <http://www.geonames.org/ontology#>
                                SELECT ?rn
                                WHERE{{
                                    ?r ns0:name ?rn .
                                }} limit {limit_query}
                                """)
        results = local_endpoint.query().bindings
        restaurants = list()
        for result in results:
            restaurants.append(result["rn"].value)

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

        restaurant = ""
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
        try:
            restaurant = mention_list[index]
            getRestInfos(dispatcher, restaurant)
        except IndexError:
            return []

        return []
