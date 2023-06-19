from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from functions.rest_infos import getRestInfos


class ResolveMention(Action):

    def name(self) -> Text:
        return "action_infos_rest_name"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        rest_name = tracker.get_slot("rest_name")
        print(rest_name)
        getRestInfos(dispatcher, rest_name)
        return []
