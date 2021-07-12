#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import os

from rdflib import Graph, Namespace
from rdflib import OWL, RDFS, Literal, BNode, XSD
from rdflib.namespace import SKOS, NamespaceManager
from rdflib.extras.describer import Describer
from rdflib.extras.infixowl import OWL_NS, Class, Property, Individual
from wordnet_mod import get_classSynset, get_propSynset
from io_utils import load_pickle_object

hoiOnto = Namespace("http://example.org/ontology/hoi/")
hoiRes = Namespace("http://example.org/resource/hoi/")
SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")

namespace_manager = NamespaceManager(Graph())
namespace_manager.bind('hoiOnto', hoiOnto, override=False)
namespace_manager.bind('hoiRes', hoiRes, override=False)
namespace_manager.bind('owl', OWL, override=False)
namespace_manager.bind("skos", SKOS, override=False)

graph = Graph()
lang = 'en'

graph.namespace_manager = namespace_manager
Individual.factoryGraph = graph

def get_hoiPairID(pairID):
    pairID += 1
    return str(pairID).zfill(6)

def get_imgID(imgID):
    imgID += 1
    return str(imgID).zfill(8)

## Create synonyms label
def synonyms(cat, d, synonym):
    if not cat.replace(" ", "_") == synonym.capitalize() :
        return d.value(SKOS.altLabel, Literal(synonym.capitalize().replace("_", " "), lang=lang))

## Create definition label
def definition(d, catDef):
    if catDef is not None:
        return d.value(SKOS.definition, Literal(catDef, datatype=XSD.string))

def get_instanceURI(insType, insURI):     ## ex)http://example.org/resource/hoi/Action/inst~
    if insURI is not None:
        return insType + "/" + insURI

## Create object and action instance
def instanceAdd(insURI, insType, insLabel, catSyn, catDef):
    d = Describer(graph, base=hoiRes)
    d.about(hoiRes.term(get_instanceURI(insType, insURI)))
    d.rdftype(hoiOnto.term(insType))
    d.value(RDFS.label, Literal(insLabel, lang=lang))
    if catSyn is not None:
        for synonym in catSyn:
            synonyms(insLabel, d, synonym)
    definition(d, catDef)

    return graph

## Create dataset source instance
def instanceDataset(insURI, insType, insLabel):
    d = Describer(graph, base=hoiRes)
    d.about(hoiRes.term(get_instanceURI(insType, insURI)))
    d.rdftype(hoiOnto.term(insType))
    if insLabel :
        d.value(RDFS.label, Literal(insLabel, lang=lang))

    return graph

## Create HOI Pair instance
def instancePairs(insURI, insType, insLabel):
    d = Describer(graph, base=hoiRes)
    d.about(hoiRes.term(insURI))
    d.rdftype(hoiOnto.term(insType))
    d.value(RDFS.label, Literal(insLabel, lang=lang))

    return graph

def init_schema(Cls, OP, DP):

    for hoiClass in Cls:
        Class(hoiOnto.term(hoiClass))
        graph.add((hoiOnto.term(hoiClass), RDFS.label, Literal(hoiClass, lang=lang)))

    ## Create and connect objectProperty
    for OProperty in OP:
        Property(hoiOnto.term(OProperty), graph=graph, baseType=OWL_NS.ObjectProperty)
        graph.add((hoiOnto.term(OProperty), RDFS.label, Literal(OProperty, lang=lang)))
        AddDomainRange().graph_add_DR(OProperty)

    ## Create and connect datatypeProperty
    graph.add((hoiOnto.hoiID, RDFS.range, XSD.string))
    for DProperty in DP:
        Property(hoiOnto.term(DProperty), graph=graph, baseType=OWL_NS.DatatypeProperty)
        graph.add((hoiOnto.term(DProperty), RDFS.label, Literal(DProperty, lang=lang)))
        graph.add((hoiOnto.term(DProperty), RDFS.domain, hoiOnto.Image))
        if DProperty == 'imageURL':
            graph.add((hoiOnto.term(DProperty), RDFS.range, XSD.anyURI))
        else:
            graph.add((hoiOnto.term(DProperty), RDFS.range, XSD.string))

    return graph

class AddDomainRange(object) :

    def get_domain_range(self, property):
        return {"actionPhrase": ["Action", "Action"],
                "originalForm": ["Action", "Action"],
                "hasAction": ["InteractionPairs", "Action"],
                "hasObject": ["InteractionPairs", "Object"],
                "definedBy": ["InteractionPairs", "InteractionSource"],
                "isPairWithObject": ["Action", "Object"],
                "isPairWithAction": ["Object", "Action"],
                "hasSuperCategory": ["Object", "ObjectSuperCategory"],
                "hasPair": ["InteractionPairs", "Image"]}[property]

    ## Define domain and ragne of objectProperty
    def graph_add_DR(self, property):
        dom, rang = self.get_domain_range(property)
        graph.add((hoiOnto.term(property), RDFS.domain, hoiOnto.term(dom)))
        graph.add((hoiOnto.term(property), RDFS.range, hoiOnto.term(rang)))

        return graph

class HoiCategory(object):

    def __init__(self, supCat, objCat):
        self.superCat = supCat.capitalize()            ## superCategory uppercase
        self.objectCat = objCat.capitalize()           ## objectCategory uppercase

    def categoryConstruct(self, obj_Dic):

        superInsURI = self.superCat.replace(" ", "_")
        objInsURI = self.objectCat.replace(" ", "_")

        objURI = get_instanceURI("Object", objInsURI)
        superURI = get_instanceURI("ObjectSuperCategory", superInsURI)

        ## Extract definitions and synonyms
        supCat_defin, supCat_syn = get_classSynset(self.superCat)
        objCat_defin, objCat_syn = get_classSynset(self.objectCat)

        instanceAdd(superInsURI, "ObjectSuperCategory", self.superCat, supCat_syn, supCat_defin)
        instanceAdd(objInsURI, "Object", self.objectCat, objCat_syn, objCat_defin)
        graph.add((hoiRes.term(objURI), hoiOnto.hasSuperCategory, hoiRes.term(superURI)))
        obj_Dic.update({objInsURI: hoiRes.term(objURI)})

        return graph, obj_Dic

class HoiAct(object):

    def __init__(self, action, obj, resName):
        self.action = action.capitalize()        # hold_obj
        self.obj = obj                           # [].capitalize()
        self.resName = resName.capitalize()

    def action_connection(self, superAct):

        supAct = get_instanceURI("Action", superAct)
        subAct = get_instanceURI("Action", self.action)
        graph.add((hoiRes.term(supAct), hoiOnto.actionPhrase, hoiRes.term(subAct)))
        graph.add((hoiRes.term(subAct), hoiOnto.originalForm, hoiRes.term(supAct)))

        return graph

    ## Connect with all objects for each incoming action
    def all_concat_action_object(self, superAct, act_Dic, obj_Dic):

        ## Create object instances (New incoming object)
        if self.obj :
            if self.obj not in obj_Dic.keys():
                ## Extract definitions and synonyms
                objCat_defin, objCat_syn = get_classSynset(self.obj)
                objURI = get_instanceURI("Object", self.obj)
                instanceAdd(self.obj, "Object", self.obj, objCat_syn, objCat_defin)
                obj_Dic.update({self.obj: hoiRes.term(objURI)})
                for act in act_Dic.values():
                    graph.add((act, hoiOnto.isPairWithObject, obj_Dic.get(self.obj)))
                    graph.add((obj_Dic.get(self.obj), hoiOnto.isPairWithAction, act))

        if superAct not in act_Dic.keys():
            act_Dic.update({superAct: hoiRes.term("Action/" + superAct)})
            for obj in obj_Dic.values():
                graph.add((act_Dic.get(superAct), hoiOnto.isPairWithObject, obj))
                graph.add((obj, hoiOnto.isPairWithAction, act_Dic.get(superAct)))

        if self.action not in act_Dic.keys():
            act_Dic.update({self.action: hoiRes.term("Action/" + self.action)})
            for obj in obj_Dic.values():
                graph.add((act_Dic.get(self.action), hoiOnto.isPairWithObject, obj))
                graph.add((obj, hoiOnto.isPairWithAction, act_Dic.get(self.action)))

        return graph, act_Dic, obj_Dic

    ## Create action instances (Connected the base form and phrase)
    def action_construct(self, superAct, origPhrase_Act):
        #print('superAct : ', superAct)

        instanceDataset(self.resName, "InteractionSource", self.resName)                          # Create dataset source instance  (ex)vcoco, hico)

        ## Extract definitions and synonyms of the base form
        superAct_defin, superAct_syn = get_propSynset(superAct)
        ## Extract definitions and synonyms of action phrase
        subAct_defin, subAct_syn = get_propSynset(self.action)

        ## If not action exists in origPhrase_Act key, add action to key
        if superAct not in origPhrase_Act.keys():
            actLabel = superAct.replace("_", " ")
            instanceAdd(superAct, "Action", actLabel, superAct_syn, superAct_defin)               ## Create base form of action

            if self.action == superAct:
                origPhrase_Act.update({superAct: []})                                             # Run : []
            else:
                origPhrase_Act.update({superAct: [self.action]})                                  # Hit : ['Hit_instr']
                actLabel = self.action.replace("_", " ")
                instanceAdd(self.action, "Action", actLabel, subAct_syn, subAct_defin)            ## Create action phrase
                self.action_connection(superAct)

        ## If action exists in origPhrase_Act key, append action
        else:
            if not self.action == superAct:                                                       # If it is not ex) Run-Run
                if not origPhrase_Act.get(superAct) :
                    origPhrase_Act[superAct] = [self.action]                                      # ex) When Run_on comes in, update '[[]]'
                    actLabel = self.action.replace("_", " ")
                    instanceAdd(self.action, "Action", actLabel, subAct_syn, subAct_defin)        ## Create action phrase
                    self.action_connection(superAct)                                              ## Connect base form of action and action phrase
                elif self.action not in origPhrase_Act.get(superAct):
                        origPhrase_Act[superAct].append(self.action)                              # Hit : ['Hit_instr', 'Hit_obj']
                        actLabel = self.action.replace("_", " ")
                        instanceAdd(self.action, "Action", actLabel, subAct_syn, subAct_defin)    ## Create action phrase
                        self.action_connection(superAct)                                          ## Connect base form of action and action phrase

        return graph, origPhrase_Act


class HoiPair(HoiAct):
    def __init__(self, action, obj, resName):
        HoiAct.__init__(self, action, obj, resName)

    def get_hoiPairKey(self, hoiID):
        return hoiID + "_" + str(self.action)

    def get_pairLabel(self, hoiID):
        return "hoiPair" + hoiID

    ## Connect action, source, hoiID to HOI Pair
    def insConn(self, hoiID):
        pairURI = get_instanceURI("InteractionPairs", hoiID)
        graph.add((hoiRes.term(pairURI), hoiOnto.hasAction, hoiRes.term(get_instanceURI("Action", self.action))))
        graph.add((hoiRes.term(pairURI), hoiOnto.definedBy, hoiRes.term(get_instanceURI("InteractionSource", self.resName))))
        graph.add((hoiRes.term(pairURI), hoiOnto.hoiID, Literal(hoiID, datatype=XSD.string)))

        return graph

    def pairForm(self, hoiID, object):
        pairURI = get_instanceURI("InteractionPairs", hoiID)
        instancePairs(pairURI, "InteractionPairs", self.get_pairLabel(hoiID))
        graph.add((hoiRes.term(pairURI), hoiOnto.hasObject, object))
        self.insConn(hoiID)

    def hoiPair_equivalent(self, hoiPair_Dic):

        searchAct = "_" + self.action.split('_')[0]
        searchObj = self.obj

        matchAct = [action for action, object in hoiPair_Dic.items() if searchAct in action]
        matchObj = [hoiPair_Dic.get(match) for match in matchAct]
        if searchObj in matchObj:
            matchLoc = matchObj.index(searchObj)
            equalPairID = matchAct[matchLoc].split('_')[0]

            return equalPairID

    def create_hoiPair(self, init, hoiPair_Dic):

        bnode = BNode()                 ## Blank Node
        #print(self.action)
        searchAct = "_" + self.action
        matchAct = [key for key in hoiPair_Dic.keys() if searchAct == key[key.index("_"):]]
        matchObj = [hoiPair_Dic.get(match) for match in matchAct]

        if not hoiPair_Dic and init == 't':
            pairID = 0
        else : pairID = len(hoiPair_Dic.keys())

        ## If not action exists in HOI Pair, add HOI Pair(it means there is no HOI Pair)
        if not matchAct:
            ## object is '[]' (empty list)
            if not self.obj:
                hoiID = get_hoiPairID(pairID)
                self.pairForm(hoiID, bnode)
                hoiPair_Dic.update({self.get_hoiPairKey(hoiID): '[]'})
            else:
                ## Find for similar pairs before adding HOIPair
                equalPairID = self.hoiPair_equivalent(hoiPair_Dic)

                hoiID = get_hoiPairID(pairID)
                object = get_instanceURI("Object", self.obj)
                self.pairForm(hoiID, hoiRes.term(object))
                hoiPair_Dic.update({self.get_hoiPairKey(hoiID): self.obj})
                if equalPairID :
                    graph.add((hoiRes.term(get_instanceURI("InteractionPairs", hoiID)), OWL.sameAs, hoiRes.term(get_instanceURI("InteractionPairs", equalPairID))))
                    graph.add((hoiRes.term(get_instanceURI("InteractionPairs", equalPairID)), OWL.sameAs, hoiRes.term(get_instanceURI("InteractionPairs", hoiID))))


        ## If action exists in HOI Pair, search whether an object exists.
        else:
            ## If object exists, add dataset source information (it means there is already constructed Action-Object Pair exists)
            if self.obj in matchObj:
                matObj_Loc = matchObj.index(self.obj)
                findAct = matchAct[matObj_Loc].split(sep='_')[0]
                interPair = get_instanceURI("InteractionPairs", findAct)
                resName = get_instanceURI("InteractionSource", self.resName)
                graph.add((hoiRes.term(interPair), hoiOnto.definedBy, hoiRes.term(resName)))

            ## If not object exists, add HOI Pair(it means there is no HOI Pair)
            else:
                ## Find for similar pairs before adding HOIPair
                equalPairID = self.hoiPair_equivalent(hoiPair_Dic)

                hoiID = get_hoiPairID(pairID)
                object = get_instanceURI("Object", self.obj)
                self.pairForm(hoiID, hoiRes.term(object))
                hoiPair_Dic.update({self.get_hoiPairKey(hoiID): self.obj})  # 000002_Sit_instr : Bicycle
                if equalPairID:
                    graph.add((hoiRes.term(get_instanceURI("InteractionPairs", hoiID)), OWL.sameAs,
                               hoiRes.term(get_instanceURI("InteractionPairs", equalPairID))))
                    graph.add((hoiRes.term(get_instanceURI("InteractionPairs", equalPairID)), OWL.sameAs,
                               hoiRes.term(get_instanceURI("InteractionPairs", hoiID))))

        return graph, hoiPair_Dic

class ImgsetAdd(object) :
    def __init__(self, init, file_name, imgUrl, img_insID):
        self.imgFileName = file_name
        self.imgUrl = imgUrl
        self.init = init

        if not img_insID and init == 't':
            self.imageID = get_imgID(0)
            img_insID.append(int(self.imageID))
        else :
            self.imageID = get_imgID(img_insID[0])
            img_insID[0] = int(self.imageID)

    def get_imgLabel(self, imgID):
        return "Image" + imgID

    def get_hoiPairKey(self, hoiID, actionName):
        return hoiID + "_" + str(actionName)

    ## Instance image Create
    def imgInform(self, imageID, imgName, imgCompre):
        graph.add((hoiRes.term(imageID), hoiOnto.fileName, Literal(imgName, datatype=XSD.string)))
        graph.add((hoiRes.term(imageID), hoiOnto.hasCompression, Literal(imgCompre, datatype=XSD.string)))
        if self.imgUrl is not None :
            graph.add((hoiRes.term(imageID), hoiOnto.imageURL, Literal(self.imgUrl, datatype=XSD.anyURI)))

        return graph

    def imgForm(self, imageID, imgName, imgCompre):
        imgURI = get_instanceURI("Image", imageID)                                  # imgURI :  Image/00002833
        instanceDataset(imageID, "Image", self.get_imgLabel(imageID))
        self.imgInform(imgURI, imgName, imgCompre)

        return graph

    def match_HoiPair(self, resName, hoiPair, actionName, objName):

        pairID = len(hoiPair.keys())

        bnode = BNode()

        searchAct = "_" + actionName

        researchAct = [key for key in hoiPair.keys() if searchAct == key[key.index("_"):]]
        researchObj = [hoiPair.get(match) for match in researchAct]

        # print('===================================')
        # print(searchAct, " ", objName)
        # print('researchAct :', researchAct)
        # print('researchObj :', researchObj)
        # print(actionName, " ", objName)

        # ===================================
        # _Hold   []
        # researchAct : ['000081_Hold']
        # researchObj : ['[]']
        # return 000081_Hold

        if researchAct and (objName in researchObj):                                                             # researchObj : [[]]
            matchLoc = researchObj.index(objName)
            return researchAct[matchLoc]
        else:
            hoiID = get_hoiPairID(pairID)
            if objName in researchObj :
                HoiPair(actionName, objName, resName).insConn(hoiID)
            elif objName == '[]' :
                HoiPair(actionName, objName, resName).pairForm(hoiID, bnode)
            else :
                HoiPair(actionName, objName, resName).insConn(hoiID)
                object = get_instanceURI("Object", objName)
                HoiPair(actionName, objName, resName).pairForm(hoiID, hoiRes.term(object))
            hoiKey = self.get_hoiPairKey(hoiID, actionName)
            hoiPair.update({hoiKey: objName})
            return hoiKey


    def imgConstruct(self, resName, hoiPair, hoi_action, hoi_object):

        action = hoi_action.capitalize()
        object = hoi_object.replace(" ", "_").capitalize()
        resName = resName.capitalize()

        imgName, imgCompre = self.imgFileName.split(sep='.')                        # imageName - fileName,URl split
        self.imgForm(self.imageID, imgName, imgCompre)                              # fileName, hasCompression,imageURL for images
        getPair = self.match_HoiPair(resName, hoiPair, action, object)
        getpair = getPair.split(sep='_')[0]
        imageID = get_instanceURI("Image", self.imageID)
        pair = get_instanceURI("InteractionPairs", getpair)
        graph.add((hoiRes.term(imageID), hoiOnto.hasPair, hoiRes.term(pair)))

        return graph, hoiPair