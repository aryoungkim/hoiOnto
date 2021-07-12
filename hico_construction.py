#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os.path
from io_utils import load_json_object, load_pickle_object, dump_pickle_object
from graph_utils import HoiAct, HoiPair, ImgsetAdd
from wordnet_mod import lemma_info

## Dataset Preprocessing
def preprocessing(action):
    if action == str('no_interaction'):
        return action
    else:
        act = action.split(sep='_')[0]
        lema_act = lemma_info(act)
        return lema_act

def hico_data_split(hoi):
    hoi = hoi.split(sep='/')
    return hoi[0], hoi[1]

def hico_create_action_and_pair(init, data_dir, resName, hoi_fileName):

    origPhraseAct = load_pickle_object('action_orgPhrase.pkl', compress=False)
    insID = load_pickle_object('instID.pkl', compress=False)
    hoiPair = insID['hoiPairID']
    all_act = load_pickle_object('all_act.pkl', compress=False)
    all_obj = load_pickle_object('all_obj.pkl', compress=False)

    with open(os.path.join(data_dir, 'hico', hoi_fileName)) as f:
        for line in f:
            key, obj, action = line.split()
            # hico_hois[int(key)] = action + '/' + obj

            obj = obj.capitalize().replace(" ", "_")

            pre_action = preprocessing(action).capitalize()  # ex) talk, kick, work

            hoiAct = HoiAct(action, obj, resName)
            hicoAct, origPhrase_Act = hoiAct.action_construct(pre_action, origPhraseAct)
            all_concat, all_act, all_obj = hoiAct.all_concat_action_object(pre_action, all_act, all_obj)
            hicoPair, hoiPair_Dic = HoiPair(action.capitalize(), obj, resName).create_hoiPair(init, hoiPair)

    insID['hoiPairID'].update(hoiPair_Dic)
    dump_pickle_object(origPhrase_Act, 'action_orgPhrase2.pkl', compress=False)
    dump_pickle_object(insID, 'instID2.pkl', compress=False)
    dump_pickle_object(all_act, 'all_act2.pkl', compress=False)
    dump_pickle_object(all_obj, 'all_obj2.pkl', compress=False)

    return hicoAct + all_concat + hicoPair

def hico_add_action_and_imgInfo(init, resName):

    hico_data = load_json_object('train_hico.json')  # val_vcoco.json load
    img_id = hico_data.keys()

    insID = load_pickle_object('instID2.pkl', compress=False)
    hoiPair = insID['hoiPairID']
    imgID = insID['imgID']

    for id in img_id:
        img_pair = hico_data[id]
        file_name = img_pair['file_name']
        hois = img_pair['hois']
        imgSet = ImgsetAdd(init, file_name, None, imgID)
        for hoi in hois:
            hoi_action, hoi_object = hico_data_split(hoi)  # hold_obj suitcase
            hicoimg, hoiPair = imgSet.imgConstruct(resName, hoiPair, hoi_action, hoi_object)

    insID['hoiPairID'] = hoiPair
    insID['imgID'] = imgID
    dump_pickle_object(insID, 'instID2.pkl', compress=False)

    return hicoimg
