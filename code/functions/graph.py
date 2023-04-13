from rdflib import Graph

def getGraph() -> Graph:
    g = Graph()
    g.parse("restInswitzerland.ttl", format="turtle")
    return g