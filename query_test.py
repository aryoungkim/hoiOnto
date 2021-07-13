from rdflib import Graph
import rdflib
from rdflib.namespace import DC, DCTERMS, DOAP, FOAF, SKOS, OWL, RDF, RDFS, VOID, XMLNS, XSD

graph = Graph()

# ... add some triples to g somehow ...
#graph.load("/home/aryoung/NRF/Ontology/TestOnto/test_v2.rdf", format="turtle")
#graph.load("/home/aryoung/NRF/Ontology/Vcoco.rdf", format="turtle")
graph.load("/home/aryoung/NRF/PyProject/hoiOntology/hoiOnto_fin/data/exp_hoiOnto.owl", format="xml")

VERB2ID=['carry', 'catch', 'cut_instr', 'cut_obj', 'drink', 'eat_instr', 'eat_obj', 'hit_instr', 'hit_obj', 'hold', 'jump', 'kick', 'lay', 'look', 'point', 'read', 'ride', 'run', 'sit', 'skateboard', 'ski', 'smile', 'snowboard', 'stand', 'surf', 'talk_on_phone', 'throw', 'walk', 'work_on_computer']

sparql1 = """
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX hoiOnto: <http://example.org/ontology/hoi/>
PREFIX hoiRes: <http://example.org/resource/hoi/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>

SELECT ?img ?hoiPair ?act ?obj
WHERE {
?img a hoiOnto:Image.
?img hoiOnto:hasPair ?hoiPair.
?hoiPair hoiOnto:hasAction ?act.
?hoiPair hoiOnto:hasObject ?obj.
?act rdfs:label ?act_label.
FILTER (str(?act_label)="Run")
}
ORDER BY ASC (?img)
"""
## V-coco data 전체
sparql2 = """
SELECT ?pair ?act ?obj
WHERE {
?pair a hoiOnto:InteractionPairs.
?pair hoiOnto:hasAction ?act.
?pair hoiOnto:hasObject ?obj.
?pair hoiOnto:definedBy ?resource.
?resource rdfs:label ?res_label
FILTER (STR(?res_label)="Vcoco")
}
"""

sparql3 = """
SELECT ?pair ?act ?obj
WHERE {
?pair a hoiOnto:InteractionPairs.
?pair hoiOnto:hasAction ?act.
?pair hoiOnto:hasObject ?obj.
?pair hoiOnto:definedBy ?dataRes.
?act rdfs:label ?act_label.
?dataRes rdfs:label ?dataRes_label.
FILTER (STR(?act_label)="Walk")
FILTER (STR(?dataRes_label)="Hico")
}
"""

sparql4 = """
SELECT ?pair ?act ?obj ?cID ?cID2
WHERE {
?pair a hoiOnto:InteractionPairs.
?pair hoiOnto:hasAction ?act.
?pair hoiOnto:hasObject ?obj.
?pair hoiOnto:definedBy ?resource.
?resource rdfs:label ?res_label.
?resource hoiOnto:hasObjectID ?cID.
?obj hoiOnto:definedObjectID ?cID2.
FILTER (STR(?res_label)="Vcoco" && ?cID=?cID2)
}
"""

sparql5 = """
SELECT DISTINCT ?pair ?act ?obj ?fileN ?Com ?URL
WHERE {
?pair a hoiOnto:InteractionPairs.
?pair hoiOnto:hasAction ?act.
?pair hoiOnto:hasObject ?obj.
?obj rdfs:label ?obj_label.
FILTER (STR(?obj_label)="Backpack")
OPTIONAL{
?img hoiOnto:hasPair ?Pair.
?img hoiOnto:fileName ?fileN.
?img hoiOnto:hasCompression ?Com.
?img hoiOnto:imageURL ?URL.
}
}
"""
sparql6 = """
SELECT ?pair ?act ?obj
WHERE {
?pair a hoiOnto:InteractionPairs.
?pair hoiOnto:hasAction ?act.
?pair hoiOnto:hasObject ?obj.
?pair hoiOnto:definedBy ?resource.
?resource rdfs:label ?res_label
FILTER (str(?res_label)="Hico")
}
ORDER BY ASC (?pair)
"""

sparql7 = """
SELECT ?img ?hoiPair ?act ?obj
WHERE {
?img a hoiOnto:Image.
?img hoiOnto:hasPair ?hoiPair.
?hoiPair hoiOnto:hasAction ?act.
?hoiPair hoiOnto:hasObject ?obj.
?act rdfs:label ?act_label.
?obj rdfs:label ?obj_label.
FILTER (str(?act_label)="Hit obj" && str(?obj_label)="Sports ball")
}
ORDER BY ASC (?img)
"""

sparql8 = """
SELECT ?img ?hoiPair ?act ?obj
WHERE {
?img a hoiOnto:Image.
?img hoiOnto:fileName ?fileName.
?img hoiOnto:hasPair ?hoiPair.
?hoiPair hoiOnto:hasAction ?act.
?hoiPair hoiOnto:hasObject ?obj.
?obj rdfs:label ?obj_label.
FILTER (str(?fileName)="000000195880")
}
"""

sparql9 = """
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX hoiOnto: <http://example.org/ontology/hoi/>
PREFIX hoiRes: <http://example.org/resource/hoi/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>

SELECT ?action ?o
WHERE {
?action a hoiOnto:Action.
?action skos:altLabel ?o.
?action rdfs:label ?act_label.
FILTER (str(?act_label)="Jump")
}
"""

action = "Walk"
dataset = "Hico"

sparql10 = ("""
SELECT ?fileName ?pair
WHERE {
?img a hoiOnto:Image.
?img hoiOnto:fileName ?fileName.
values  str(?fileName) {"000000000165" "000000319492" "000000581637"}
?img hoiOnto:hasPair ?pair.
}
""")
# % (action,dataset)

sparql11 = """
SELECT (count(?obj) as ?obj_count)
where{
  ?act a hoiOnto:Action;
         rdfs:label 'Hit'@en;
         hoiOnto:isPairWithObject ?obj.
}

"""

#Triple count
sparql0 = """SELECT (COUNT(*) as ?Triples)
       WHERE { ?s ?p ?o }"""

# test : query4, query5, query6, query7
for row in graph.query(sparql11):
    # print(row.s)
    # print(row.pair, row.act, row.obj, row.fileN, row.Com, row.URL)
    #print("%s %s %s" % row)
    #print(row.img, row.hoiPair, row.act, row.obj)
    # print(row.fileName, row.pair)
    # print(row.action,row.o)
    # print(row.pair, row.act, row.obj, row.cID, row.cID2)
    print(row.obj_count)
    # print(row.oP, row.o)
    # print(row.s, row.p, row.o)


# q = prepareQuery(
# '''
# SELECT ?Pair WHERE {
# ?Pair hoiOnto:definedBy ?Dataset.
# ?Dataset rdfs:label "Hico"@en.
# }''' , initNs = {"hoiOnto": hoiOnto})
#
# g = rdflib.Graph()
#
# g.parse('/home/aryoung/NRF/Graph/Ontology/TestOnto/test_v4.rdf', format="turtle")
#
# tim = rdflib.URIRef("http://example.org/resource/hoi/InteractionPairs/")
# for row in g.query(q, initBindings={'Pair': tim}):
#     print(row)

fileName = "546"
dataset = "Vcoco"

queryString2 = ("""
PREFIX hoiRes: <http://example.org/resource/hoi/>
PREFIX hoiOnto: <http://example.org/ontology/hoi/>

SELECT ?img ?hoiPair ?act_label ?obj_label
WHERE {
?img a hoiOnto:Image.
?img hoiOnto:fileName ?fileName.
FILTER regex(str(?fileName),"%s")
?img hoiOnto:hasPair ?hoiPair.
?hoiPair hoiOnto:hasAction ?act.
?hoiPair hoiOnto:hasObject ?obj.
?hoiPair hoiOnto:definedBy ?resource.
?resource rdfs:label ?res_label
FILTER (?res_label != "%s")
optional{
?act rdfs:label ?act_label.
?obj rdfs:label ?obj_label.
}
}
""") % (fileName, dataset)

# for row in graph.query(queryString2):
#     print(row.img, row.hoiPair, row.act_label, row.obj_label)
