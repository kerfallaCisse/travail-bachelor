from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from .allInfosWithMention_actions import local_endpoint
from SPARQLWrapper import SPARQLWrapper2, BASIC
from .restaurantsInCity_actions import osmap_endpoint
from rdflib import Namespace, URIRef, Graph


CUISINE = {
    "afghan": "afghan", "africain": "african", "américaine": "american", "arabe": "arab", "arabesque": "arabe", "argentin": "argentinian", "arménien": "armenian",
    "asiatique": "asian", "asiate": "asian", "australien": "australian", "austrien": "austrian", "belge": "belgian", "bolivien": "bolivian", "brésilien": "brazilian", "britanique": "british",
    "bulgarien": "bulgarian", "chinois": "chinese", "colombien": "colombian", "croate": "croatian", "cubain": "cuban", "égyptien": "egyptian", "éthiopien": "ethiopian", "européen": "european", "français": "french",
    "allemand": "german", "indien": "indian", "italien": "italian", "japonais": "japanese", "coréen": "corean", "mexicain": "mexican", "marocain": "maroccan", "pakistanais": "pakistan", "portugais": "portuguese", "russe": "russian",
    "espagnol": "spanish", "suisse": "swiss", "thailandais": "thai", "sénégalais": "senegalese",
    "australienne": "australian", "africaine": "african", "afghane": "afghan", "américaine": "american", "argentine": "argentinian", "arménienne": "armenian", "austrienne": "austrian", "bolivienne": "bolivian", "brésilienne": "brazilian",
    "bulgarienne": "bulgarian", "chinoise": "chinese", "colombienne": "colombian", "croatienne": "croatian", "cubaine": "cuban", "égyptienne": "egyptian", "éthiopienne": "ethiopian", "européenne": "european", "française": "french", "allemande": "german",
    "indienne": "indian", "italienne": "italian", "japonaise": "japanese", "coréenne": "corean", "mexicaine": "mexican", "marocaine": "maroccan", "pakistanaise": "pakistan", "portugaise": "portuguese", "thailandaise": "thai", "sénégalaise": "senegalese"
}


class RestTypeCuisine(Action):
    def name(self) -> Text:
        return "action_cuisine_type"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        limit = tracker.get_slot("query_limit")
        city = tracker.get_slot("city")
        type_cuisine = tracker.get_slot("type_cuisine")
        
        dispatcher.utter_message(text=f"Type de cuisine: {type_cuisine}; Ville: {city}; Limit: {limit}")
        
        
        

        return []
