from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from SPARQLWrapper import SPARQLWrapper2
from functions.rest_infos import getRestInfos

sparql_dbpedia = SPARQLWrapper2(
    "https://dbpedia.org/sparql")  # DBpedia endpoint
local_endpoint = SPARQLWrapper2(
    "http://localhost:7200/repositories/POC-1")  # my local graphDB endpoint


class ResolveMention(Action):

    def name(self) -> Text:
        return "action_infos_rest_name"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        rest_name = tracker.get_slot("rest_name")
        getRestInfos(dispatcher, rest_name)
        return []
