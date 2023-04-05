# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
from SPARQLWrapper import SPARQLWrapper2
import sys
from functions.resolve_mention import mapping
sys.path.insert(0, "/code/functions")


sparql = SPARQLWrapper2("https://dbpedia.org/sparql") #DBpedia endpoint


class ListerRestaurants(Action):

    def name(self) -> Text:
        return "action_lister_restaurants"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        sparql.setQuery("""
                        select distinct ?rn
                        where {
                        ?r dbo:wikiPageWikiLink dbc:Restaurants_in_Switzerland .
                        ?r rdfs:label ?rn .
                        FILTER(lang(?rn) = 'fr' || lang(?rn) = 'en' || lang(?rn) = 'de')
                        } limit 30
                        """)
        response = sparql.query().bindings

        if len(response) == 0:
            return dispatcher.utter_message(text="Nous n'avons pas trouvé de restaurant dans ce pays")

        response_to_return = ""
        restaurants = set()

        for result in response:
            restaurant_name = result['rn'].value
            restaurants.add(restaurant_name)
        
        restaurants.remove("List of restaurants in Switzerland")
        
        
        for rn in restaurants:
            response_to_return += "- " + rn + "\n"
     
        response_to_return += "..."
        
        dispatcher.utter_message(text=response_to_return)
        
        return [SlotSet('mention_list', list(restaurants))]


class ResolveMention(Action):

    def name(self) -> Text:
        return "action_resolve_mention"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        mention_list = tracker.get_slot('mention_list')
        #print("mention list : ", mention_list)
        #print(type(mention_list))
        mention = tracker.get_slot('mention')
        #print("mention : ", mention)
        
        # mapping
        index = mapping(mention)
        #print('mapping index :', index)
        
        restaurant = mention_list[index]
        
        
        dispatcher.utter_message(text=f"Tu veux les informations de ce restaurant {restaurant}")
        
        return []
    
