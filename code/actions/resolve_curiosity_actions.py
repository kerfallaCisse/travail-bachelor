from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher


class ResolveCuriosity(Action):

    def name(self) -> Text:
        return "action_resolve_curiosity"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        rest_name = tracker.get_slot("rest_name")
        limit = tracker.get_slot("query_limit")
        dispatcher.utter_message(
            text=f"Tu veux les curiosités du restaurant : {rest_name}: limit: {limit}")

        return []
