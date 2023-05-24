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
        # dispatcher.utter_template(
        #     "utter_please_rephrase", tracker, link=linkOfdocumentation)
        dispatcher.utter_message(
            response="utter_please_rephrase", link=linkOfdocumentation)
        return [UserUtteranceReverted()]


class SetQueryLimitationIntent(Action):
    def name(self) -> Text:
        return "action_set_limit_intent"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        dispatcher.utter_message(
            text="Combien ?")

        intent = tracker.get_intent_of_latest_message()
        if intent == "lister_restaurants":
            return [SlotSet("rest_ville", False)]
        elif intent == "restaurants_city":
            return [SlotSet("rest_ville", True)]
        elif intent == "restaurant_curiosity":
            return [SlotSet("limit_curiosity", True)]

        return []


class SetQueryLimitation(Action):
    def name(self) -> Text:
        return "action_set_nbr_rest"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        limit = tracker.get_slot("query_limit")
        if not limit:
            return []
        return [SlotSet("limit_nbr_rest", limit)]
