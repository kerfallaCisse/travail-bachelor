from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import UserUtteranceReverted, SlotSet


class FallBackAction(Action):

    def name(self) -> Text:
        return "action_fallback"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        """On exécute le fallback action et on revient l'état précédent de la conversation"""
        linkOfdocumentation = "http://127.0.0.1:8080/documentation"
        dispatcher.utter_template(
            "utter_please_rephrase", tracker, link=linkOfdocumentation)
        return [UserUtteranceReverted()]


class SetQueryLimitation(Action):
    def name(self) -> Text:
        return "action_set_rest_limit"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        limit = tracker.get_slot("query_limit")
        print(limit)

        return [SlotSet("limit_nbr_rest", limit)]
