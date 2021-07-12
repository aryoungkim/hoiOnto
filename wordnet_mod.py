#!/usr/bin/env python
# -*- coding: utf-8 -*-

from nltk.corpus import wordnet as wn
from nltk.stem.wordnet import WordNetLemmatizer

def get_classSynset(getCat) :

    getCat = getCat.replace(" ", "_")  ## nameEntity 공백 변환
    #print(getCat)

    synset = wn.synsets(getCat)
    if len(synset) > 0:
        synset = synset[0]
        definition, synonyms = synset_info(synset)
        return definition, synonyms
    else:
        return None, None

def get_propSynset(getCat) :

    #print(getCat)
    synset = wn.synsets(getCat)
    if len(synset) > 0 and wn.synsets(getCat, pos=wn.VERB):
        synset = wn.synsets(getCat, pos=wn.VERB)[0]
        definition, synonyms = synset_info(synset)
        return definition, synonyms
    else : return None, None

def synset_info(synset) :
    definition = synset.definition()
    #synonyms = ", ".join([lem.name() for lem in synset.lemmas()])
    synonyms = synset.lemma_names()

    return definition, synonyms

def lemma_info(getAct):
    syns = wn.synsets(getAct.lower(), 'v')
    nltlema = WordNetLemmatizer()
    if syns:                                        ## 동사 원형 추출
        syn_list = [syn.name() for syn in syns]
        mat_syn = [s.split('.')[0] for s in syn_list]
        if getAct in mat_syn:
            matchID = mat_syn.index(getAct)
            lema = syns[matchID].lemmas()[0].name()
        else : lema = nltlema.lemmatize(getAct.lower(), 'v')
    else:                                          ## 표제어 추출   (text의 경우 동사 원형이 안나옴)
        lema = nltlema.lemmatize(getAct.lower(), 'v')

    return lema

