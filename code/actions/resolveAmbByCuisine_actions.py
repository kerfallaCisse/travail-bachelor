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

        restaurants = {}

        LAT_URI = "http://www.w3.org/2003/01/geo/wgs84_pos#lat"
        LONG_URI = "http://www.w3.org/2003/01/geo/wgs84_pos#long"
        CUISINE_URI = "http://restaurant#cuisine"
        CITY_URI = "http://restaurant#city"
        ADRESSE_URI = "http://restaurant#adresse"
        POSTCODE_URI = "http://restaurant#postcode"
        OPENING_HOURS_URI = "http://restaurant#opening_hours"

        type_cuisines = list(set(tracker.get_slot("type_cuisine")))
        rest_name = tracker.get_slot("rest_name")
        QUERY = "PREFIX ns0: <http://www.geonames.org/ontology#>\nPREFIX r: <http://restaurant#>\nSELECT ?rn WHERE { ?r r:cuisine "
        QUERY_ALL_INFOS = f"prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>\nprefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>\nprefix ns0: <http://www.geonames.org/ontology#>\nprefix dbpedia: <http://dbpedia.org/resource/>\nprefix r: <http://restaurant#>\n"
        QUERY_ALL_INFOS += "SELECT ?r ?p ?o\nWHERE { ?r ns0:name " + \
            f"'{rest_name}' ; r:cuisine "
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
                QUERY_ALL_INFOS += f"'{cuisine_english}' ; ?p ?o . \n" + \
                    "FILTER (?p != rdfs:isDefinedBy && ?p != ns0:featureClass && ?p != ns0:featureCode && ?p != ns0:countryCode && ?p != ns0:parentCountry && ?p != ns0:name && ?p != rdf:type)\n}"
            else:
                QUERY += f"'{cuisine_english}' , "
                QUERY_ALL_INFOS += f"'{cuisine_english}' , "
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
            local_endpoint.setQuery(query=QUERY_ALL_INFOS)
            response_all_infos = local_endpoint.query().bindings
            if len(response_all_infos) == 0:
                dispatcher.utter_message(
                    text="Désolé nous n'avons trouvé aucun restaurant qui propose ces spécialités")
                return []
            for rp_ainfos in response_all_infos:
                subj = rp_ainfos["r"].value
                pred = rp_ainfos["p"].value
                obj = rp_ainfos["o"].value
                if subj not in restaurants:
                    restaurants[subj] = {}
                    subj_values: dict = restaurants.get(subj)
                    if pred.find("cuisine") > -1:
                        subj_values[pred] = [obj]
                    else:       
                        subj_values[pred] = obj
                    restaurants[subj] = subj_values
                else:
                    subj_values: dict = restaurants.get(subj)
                    if pred.find("cuisine") > -1:
                        specialities = subj_values.get(pred,None)
                        if specialities is not None:
                            specialities.append(obj)
                            subj_values[pred] = specialities
                    else:
                        subj_values[pred] = obj    
                    restaurants[subj] = subj_values
            i = 1    
            for _, v in restaurants.items():
                dispatcher.utter_message(text=f"--------------------{i}--------------------")
                latitude = v.get(LAT_URI, None)
                longitude = v.get(LONG_URI, None)
                rest_cuisine: list = v.get(CUISINE_URI, None)
                city = v.get(CITY_URI, None)
                adresse = v.get(ADRESSE_URI, None)
                postcode = v.get(POSTCODE_URI, None)
                opening_hours = v.get(OPENING_HOURS_URI, None)
                if latitude is not None:
                    dispatcher.utter_message(text=f"- Latitude: {latitude}")
                if longitude is not None:
                    dispatcher.utter_message(text=f"- Longitude: {longitude}")
                if adresse is not None:
                    dispatcher.utter_message(text=f"- Rue: {adresse}")   
                if postcode is not None:
                    dispatcher.utter_message(text=f"- Code postale: {postcode}")
                if opening_hours is not None:
                    dispatcher.utter_message(text=f"- Horaires d'ouverture: {opening_hours}")
                if city is not None:
                    dispatcher.utter_message(text=f"- Ville: {city}")
                if rest_cuisine is not None:
                    c = ";".join(rest_cuisine)
                    dispatcher.utter_message(text=f"- Spécialité: {c}")
                i += 1
                    
        else:
            getRestInfos(dispatcher, rest_name,
                         cuisine=type_cuisines, cuisine_mapping=CUISINE)

        return []
