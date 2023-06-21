from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

class ResolveAmbByTypeCuisine(Action):
    def name(self) -> Text:
        return "action_ramb_cuisine"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        type_cuisines = set(tracker.get_slot("type_cuisine"))
        rest_name = tracker.get_slot("rest_name")
        
        # On génère la requete Sparal; etc
        dispatcher.utter_message(text=f"Tu cherches les types de cuisine suivants: , du restaurant {rest_name}")

        return []