from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from .allInfosWithMention_actions import local_endpoint
from .restTypeCuisine_actions import CUISINE
from functions.rest_infos import getRestInfos


class ResolveAmbByTypeCuisine(Action):
    def name(self) -> Text:
        return "action_ramb_cuisine"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        type_cuisines = list(set(tracker.get_slot("type_cuisine")))
        rest_name = tracker.get_slot("rest_name")
        QUERY = "PREFIX ns0: <http://www.geonames.org/ontology#>\nPREFIX r: <http://restaurant#>\nSELECT ?rn WHERE { ?r r:cuisine "

        type_cuisines_size = len(type_cuisines)
        for i in range(type_cuisines_size):
            cuisine = type_cuisines[i]
            cuisine_english = CUISINE.get(cuisine, None)
            if cuisine_english is None:
                dispatcher.utter_message(
                    text="Oups, désolé, nous n'avons pas trouvé les spécialités mentionnées")
                return []
            if i == type_cuisines_size - 1:
                QUERY += f"'{cuisine_english}' ; ns0:name ?rn . FILTER(?rn = '{rest_name}') ." + "\n}"
            else:
                QUERY += f"'{cuisine_english}' , "
        local_endpoint.setQuery(query=QUERY)
        response = local_endpoint.query().bindings
        response_size = len(response)
        if response_size == 0:
            dispatcher.utter_message(
                text="Oups, désolé, nous n'avons trouvé aucun restaurant")
            return []
        elif response_size > 1:
            dispatcher.utter_message(
                text=f"J'ai trouvé {response_size} restaurants ayant le même nom et proposant les mêmes spécialités. Voici les informations concernant ces restaurants:")
            # On affiche les informations de chaque restaurant
            for _ in response:
                getRestInfos(dispatcher, rest_name,
                             cuisine=type_cuisines, cuisine_mapping=CUISINE, resolving_amb=True)
                dispatcher.utter_message(text=">>>>>>>>>>>>>>>>>")
        else:
            getRestInfos(dispatcher, rest_name,
                         cuisine=type_cuisines, cuisine_mapping=CUISINE, resolving_amb=True)

        return []
