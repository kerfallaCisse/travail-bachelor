# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from SPARQLWrapper import SPARQLWrapper, JSON
from SPARQLWrapper import SPARQLWrapper2



sparql = SPARQLWrapper("http://localhost:7200/repositories/POC-1")
sparql2 = SPARQLWrapper2("http://localhost:7200/repositories/POC-1")

class ListerRestaurants(Action):
    

    def name(self) -> Text:
        return "action_lister_restaurants"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
            
        sparql.setQuery("""
                        prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> 
                        prefix r: <http://www.ressource.com/restaurant/> 
                        prefix foaf: <http://xmlns.com/foaf/0.1/> 
                        select ?rn
                        where {
                            ?r rdf:type r:Restaurant .
                            ?r foaf:name ?rn
                        }
                        """)
        
        
        sparql.setReturnFormat(JSON)
        response = sparql.query().convert()
        
        listOf_restaurants = list()
        
        for json_object in response["results"]["bindings"]:
            for _,v in json_object.items():
                listOf_restaurants.append(v["value"])
                    
        response_to_return = "\n".join(listOf_restaurants)
        dispatcher.utter_message(text=f"{response_to_return}")

        return []

class ListerRestaurantsPays(Action):
        
    def name(self) -> Text:
        return "action_lister_restaurants_pays"
        

    def run(self, dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        nom_pays = tracker.get_slot("nom_pays")
        print(nom_pays)
        
        sparql2.setQuery(f'''
                         PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                         PREFIX r: <http://www.ressource.com/restaurant/>
                         prefix foaf: <http://xmlns.com/foaf/0.1/> 
                         PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
                         select ?rn
                         where {{
                             ?r rdf:type r:Restaurant .
                             ?r foaf:place "{nom_pays}"^^xsd:string .
                             ?r foaf:name ?rn .
                         }}
                         ''')
           
        # la réponse est déjà au format json
        response = sparql2.query().bindings
        print(response)
        if len(response)==0:
            dispatcher.utter_message(text="désolé nous n'avons aucune information sur ce pays")
            return []
        
        response_to_return = ""
        for result in response:
            response_to_return +=  "- " + result["rn"].value + "\n"
        
        dispatcher.utter_message(text=response_to_return)
                   
        return []
    
class ListerRestaurantsTranchePrix(Action):
    def name(self) -> Text:
        return "action_lister_restaurants_tranche_prix"
    
    def run(self, dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        nom_pays = tracker.get_slot("nom_pays")
        print(nom_pays)
        tranche_prix = tracker.get_slot("tranche_prix")
        print(tranche_prix)
        
        sparql2.setQuery(f"""
                         PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                         PREFIX r: <http://www.ressource.com/restaurant/>
                         prefix foaf: <http://xmlns.com/foaf/0.1/> 
                         PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
                         select ?rn
                         where {{
                            ?r rdf:type r:Restaurant .
                            ?r foaf:place "{nom_pays}"^^xsd:string .
                            ?r foaf:pricing_range "{tranche_prix}"^^xsd:string .
                            ?r foaf:name ?rn 
                         }}
                         """)
        
        response = sparql2.query().bindings
        
        if len(response) == 0:
            dispatcher.utter_message(text=f"Désolé nous n'avons trouver aucun restaurant {tranche_prix}")
            return []
        
        response_to_return = ""
        for result in response:
            response_to_return +=  "- " + result["rn"].value + "\n"
        
        dispatcher.utter_message(text=response_to_return)
                   
        return []

    
    