from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from .allInfosWithMention_actions import local_endpoint
from SPARQLWrapper import SPARQLWrapper2, BASIC
from .restaurantsInCity_actions import osmap_endpoint
from rdflib import Namespace, URIRef, Graph

graph = Graph()


class ResolveCuriosity(Action):

    def name(self) -> Text:
        return "action_resolve_curiosity"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        rest_name = tracker.get_slot("rest_name")
        limit = tracker.get_slot("query_limit")
        if int(limit) > 20:
            dispatcher.utter_message(response="utter_limit")
            return []
        
        # On récupère la longitute et la latitude du restaurant ainsi que l'uri du restaurant
        local_endpoint.setQuery(f"""
                                PREFIX r: <http://restaurant#>
                                PREFIX geo1: <http://www.w3.org/2003/01/geo/wgs84_pos#>
                                PREFIX ns0: <http://www.geonames.org/ontology#>
                                SELECT ?rest ?long ?lat ?cu
                                WHERE {{
                                    ?rest ns0:name "{rest_name}" ;
                                          geo1:long ?long ;
                                          geo1:lat ?lat .
                                    OPTIONAL {{
                                        ?rest r:curiosity ?cu .
                                    }}      
                                }} limit {limit}
                                """)
        resp = local_endpoint.query().bindings
        curiosities = []
        if len(resp) == 0:
            dispatcher.utter_message(
                text="Désolé nous n'avons aucune curiosité sur ce restaurant.")

        else:
            response = resp[0]
            rest_ressource = response["rest"].value
            for rp in resp:
                try:
                    curiosities.append(rp["cu"].value)
                except Exception:
                    continue
            if len(curiosities) == 0:
                # On interroge open street map pour récupérer les curiosités du restaurant en question
                latitude = response["lat"].value
                longitude = response["long"].value
                POINT = f"Point({longitude} {latitude})"
                try:
                    osmap_endpoint.setTimeout(120)
                    osmap_endpoint.setQuery(f"""
                                            SELECT * 
                                            WHERE {{
                                                ?osm_objects osmt:leisure "pitch" . # terrain
                                                SERVICE wikibase:around {{ 
                                                        ?osm_objects osmm:loc ?coordinates. 
                                                        bd:serviceParam wikibase:center "{POINT}"^^geo:wktLiteral.
                                                        bd:serviceParam wikibase:radius "1". # kilomètre -> distance maximale
                                                        bd:serviceParam wikibase:distance ?distance .
                                                    }}   
                                            }} limit {limit}                                            
                                            """)

                    response_endpoint = osmap_endpoint.query().bindings
                    if len(response_endpoint) == 0:
                        dispatcher.utter_message(
                            text="Désolé nous n'avons trouvé aucune curiosité autour de ce restaurant")
                        return []
                    for rep_endpt in response_endpoint:
                        curiosities.append(rep_endpt["osm_objects"].value)
                    if len(curiosities) != 0:
                        local_endpointAddStmnt = SPARQLWrapper2(
                            "http://localhost:7200/repositories/POC-1/statements")
                        local_endpointAddStmnt.setHTTPAuth(BASIC)
                        local_endpointAddStmnt.queryType = "INSERT"
                        local_endpointAddStmnt.setCredentials("", "")
                        local_endpointAddStmnt.method = "POST"
                        local_endpointAddStmnt.setReturnFormat("json")
                        R = Namespace("http://restaurant#")
                        curiosity_ressource = R.curiosity
                        restRessource = URIRef(rest_ressource)
                        graph.bind("r", R)
                        for cu in curiosities:
                            local_endpointAddStmnt.setQuery(f"""
                                                            PREFIX r: <http://restaurant#>
                                                            INSERT DATA {{
                                                                <{rest_ressource}> r:curiosity <{cu}> .
                                                            }}
                                                            """)
                            local_endpointAddStmnt.query()
                            correspondingCuriosity = URIRef(cu)
                        # On ajoute dans le fichier turtle
                            graph.add(
                                (restRessource, curiosity_ressource, correspondingCuriosity))
                        graph.parse(source="restInswitzerland.ttl")
                        graph.serialize(
                            destination="restInswitzerland.ttl", format="ttl")    

                except TimeoutError:
                    dispatcher.utter_message(
                        text="Désolé, la requête prend plus de temps que prévu. Reposez votre question.")
                    return []

        if len(curiosities) != 0:
            respToReturn = "\n".join(curiosities)
            dispatcher.utter_message(text=respToReturn)
        return []
