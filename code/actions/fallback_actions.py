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
        linkOfdocumentation = "http://127.0.0.1:5000/documentation"
        dispatcher.utter_message(
            response="utter_please_rephrase", link=linkOfdocumentation)
        return [UserUtteranceReverted()]


class SetQueryLimitationIntent(Action):
    def name(self) -> Text:
        return "action_set_limit_intent"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        question_rest = "Combien de restaurant ?"
        question_curiosity = "Combien de curiosité/activité ?"

        intent = tracker.get_intent_of_latest_message()
        if intent == "lister_restaurants":
            dispatcher.utter_message(text=question_rest)
            return [SlotSet("rest_ville", False)]
        elif intent == "restaurants_city":
            dispatcher.utter_message(text=question_rest)
            return [SlotSet("rest_ville", True)]
        elif intent == "restaurant_curiosity":
            dispatcher.utter_message(text=question_curiosity)
            return [SlotSet("limit_curiosity", True)]
        elif intent == "rest_cuisine":
            dispatcher.utter_message(text=question_rest)
            return [SlotSet("cuisine_type", True)]

        return []
