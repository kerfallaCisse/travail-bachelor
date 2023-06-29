from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from .allInfosWithMention_actions import local_endpoint
from .restaurantsInCity_actions import osmap_endpoint
from rdflib import Namespace, URIRef, Graph, Literal
from rasa_sdk.events import SlotSet
from .allInfosWithMention_actions import local_endpoint
from .restaurantsInCity_actions import osmap_endpoint, local_endpoint_add_stmnt

g = Graph()

CUISINE = {
    "afghan": "afghan", "africain": "african", "américaine": "american", "arabe": "arab", "arabesque": "arabe", "argentin": "argentinian", "arménien": "armenian",
    "asiatique": "asian", "asiate": "asian", "australien": "australian", "austrien": "austrian", "belge": "belgian", "bolivien": "bolivian", "brésilien": "brazilian", "britanique": "british",
    "bulgarien": "bulgarian", "chinois": "chinese", "colombien": "colombian", "croate": "croatian", "cubain": "cuban", "égyptien": "egyptian", "éthiopien": "ethiopian", "européen": "european", "français": "french",
    "allemand": "german", "indien": "indian", "italien": "italian", "japonais": "japanese", "coréen": "corean", "mexicain": "mexican", "marocain": "maroccan", "pakistanais": "pakistan", "portugais": "portuguese", "russe": "russian",
    "espagnol": "spanish", "suisse": "swiss", "thailandais": "thai", "sénégalais": "senegalese",
    "australienne": "australian", "africaine": "african", "afghane": "afghan", "américaine": "american", "argentine": "argentinian", "arménienne": "armenian", "austrienne": "austrian", "bolivienne": "bolivian", "brésilienne": "brazilian",
    "bulgarienne": "bulgarian", "chinoise": "chinese", "colombienne": "colombian", "croatienne": "croatian", "cubaine": "cuban", "égyptienne": "egyptian", "éthiopienne": "ethiopian", "européenne": "european", "française": "french", "allemande": "german",
    "indienne": "indian", "italienne": "italian", "japonaise": "japanese", "coréenne": "corean", "mexicaine": "mexican", "marocaine": "maroccan", "pakistanaise": "pakistan", "portugaise": "portuguese", "thailandaise": "thai", "sénégalaise": "senegalese",
    "libanaise":"lebanese", "libanais":"lebanese"
}


class RestTypeCuisine(Action):

    def name(self) -> Text:
        return "action_cuisine_type"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        city = tracker.get_slot("city")
        cuisine_slot = tracker.get_slot("type_cuisine")
        type_cuisine = ""
        limit = tracker.get_slot("query_limit")
        mention_list = set()
        
        if int(limit) > 20:
            dispatcher.utter_message(response="utter_limit")
            return []
        
        try:
            type_cuisine = cuisine_slot[0]
        except Exception:
            return []   

        cuisine_english = CUISINE.get(type_cuisine, None)
        if cuisine_english is None:
            dispatcher.utter_message(
                text="Désolé nous ne traitons pas ce type de cuisine. Veuillez reéssayer avec un autre type de cuisine.")
            return []

        # On récupère les restaurants dans le graph
        local_endpoint.setQuery(f"""
                                PREFIX r: <http://restaurant#>
                                PREFIX ns0: <http://www.geonames.org/ontology#>
                                SELECT ?rn
                                WHERE {{
                                    ?r r:cuisine "{cuisine_english}" ;
                                       r:city "{city}" ;
                                       ns0:name ?rn .     
                                }} limit {limit}
                                """)

        resp = local_endpoint.query().bindings
        if len(resp) == 0:
            # On requête open street map pour obtenir des restaurants avec
            osmap_endpoint.setQuery(f"""
                                    SELECT *
                                    WHERE {{
                                        VALUES ?type {{"bar" "restaurant" "pub" "cafe" "food_court" "biergarten" "fast_food"}}
                                        ?osmn osmt:addr:city "{city}" ;
                                              osmt:amenity ?type ;
                                              osmm:loc ?loc ;
                                              osmt:name ?name ;
                                              osmt:cuisine "{cuisine_english}" ;
                                              osmt:addr:street ?street .
                                        BIND(geof:longitude(?loc) as ?longitude)
                                        BIND(geof:latitude(?loc) as ?latitude)
                                        OPTIONAL {{
                                            ?osmn osmt:opening_hours ?hours .
                                        }}
                                        OPTIONAL {{
                                            ?osmn osmt:addr:postcode ?postcode .
                                        }}       
                                    }} limit {limit}
                                    """)
            resp_osmap = osmap_endpoint.query().bindings
            if len(resp_osmap) == 0:
                dispatcher.utter_message(
                    text=f"Désolé nous n'avons pas trouvé de restaurant {type_cuisine} dans cette ville.")
                return []

            R_NAMESPACE = Namespace("http://restaurant#")
            cuisine = R_NAMESPACE.cuisine
            opening_hours = R_NAMESPACE.opening_hours
            postal_code = R_NAMESPACE.postcode
            adresse = R_NAMESPACE.adresse
            r_city = R_NAMESPACE.city
            GE01_NAMESPACE = Namespace(
                "http://www.w3.org/2003/01/geo/wgs84_pos#")
            geo_lat = GE01_NAMESPACE.lat
            geo_long = GE01_NAMESPACE.long
            NS0_NAMESPACE = Namespace("http://www.geonames.org/ontology#")
            ns0_name = NS0_NAMESPACE.name
            i = 0
            for rest in resp_osmap:
                longitude = rest["longitude"].value
                latitude = rest["latitude"].value
                rue = rest["street"].value
                rest_name = rest["name"].value
                osmn = rest["osmn"].value
                hours = ""
                postcode = ""
                OSMN = URIRef(osmn)
                mention_list.add(rest_name)

                try:
                    hours = rest["hours"].value 
                    postcode = rest["postcode"].value
                except KeyError:
                    pass
                i += 1
                dispatcher.utter_message(
                    text=f"{i}\n- Nom: {rest_name}\n- Longitude: {longitude}\n- Latitude: {latitude}\n- Rue: {rue}")
                if len(hours) != 0:
                    dispatcher.utter_message(text=f"- Horraires: {hours}")
                if len(postcode) != 0:
                    dispatcher.utter_message(text=f"Code postale: {postcode}")

                # On vérifi si le restaurant existe dans le graphe
                local_endpoint.setQuery(f"""
                                        PREFIX ns0: <http://www.geonames.org/ontology#>
                                        SELECT *
                                        WHERE {{
                                            ?r ns0:name "{rest_name}" .
                                        }}
                                        """)
                if len(local_endpoint.query().bindings) == 0:
                    # On enregistre le restaurant pour l'extraction des entités
                    with open("data/rest_name.txt", "a", encoding="utf-8") as f:
                        f.write(rest_name+"\n")
                    # On crée les tuples
                    local_endpoint_add_stmnt.setQuery(f"""
                                                      PREFIX ns0: <http://www.geonames.org/ontology#>
                                                      PREFIX geo1: <http://www.w3.org/2003/01/geo/wgs84_pos#>
                                                      PREFIX r: <http://restaurant#>
                                                      INSERT DATA {{
                                                          <{osmn}> a <https://www.openstreetmap.org/node/> ;
                                                                   ns0:name "{rest_name}" ;
                                                                   geo1:lat "{latitude}" ;
                                                                   geo1:long "{longitude}" ;
                                                                   r:cuisine "{type_cuisine}" ;
                                                                   r:adresse "{rue}" ;
                                                                   r:city "{city}" .
                                                      }}
                                                      """)
                    local_endpoint_add_stmnt.query()
                    g.add((OSMN, ns0_name, Literal(rest_name)))
                    g.add((OSMN, geo_lat, Literal(latitude)))
                    g.add((OSMN, geo_long, Literal(longitude)))
                    g.add((OSMN, cuisine, Literal(type_cuisine)))
                    g.add((OSMN, adresse, Literal(rue)))
                    g.add((OSMN, r_city, Literal(city)))
                    if len(hours) != 0:
                        local_endpoint_add_stmnt.setQuery(f"""
                                                          PREFIX r: <http://restaurant#>
                                                          INSERT DATA {{
                                                              <{osmn}> r:opening_hours "{hours}" .
                                                          }}
                                                          """)
                        local_endpoint_add_stmnt.query()
                        g.add((OSMN, opening_hours, Literal(hours)))
                    if len(postcode) != 0:
                        local_endpoint_add_stmnt.setQuery(f"""
                                                          PREFIX r: <http://restaurant#>
                                                          INSERT DATA {{
                                                              <{osmn}> r:postcode "{postcode}" .
                                                          }}
                                                          """)
                        local_endpoint_add_stmnt.query()
                        g.add((OSMN, postal_code, Literal(postcode)))
            g.parse(source="data/restInswitzerland.ttl")
            g.serialize(destination="data/restInswitzerland.ttl", format="ttl")

        else:
            for r in resp:
                restName = r["rn"].value    
                mention_list.add(restName)
        mention_list_size = len(mention_list)
        mention_list = list(mention_list)        
        if mention_list_size != 0:
            for i in range(mention_list_size):
                corresponding_rest = mention_list[i]
                i += 1
                dispatcher.utter_message(text=f"{i}- {corresponding_rest}")
            return [SlotSet("mention_list", mention_list)]
        return []
