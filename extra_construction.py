#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os.path
from io_utils import load_json_object, load_pickle_object, dump_pickle_object
from graph_utils import HoiAct, HoiPair, ImgsetAdd
from wordnet_mod import lemma_info

## Dataset Preprocessing
def preprocessing(action):
    if action == str('No_interaction'):
        return action
    else:
        act = action.split(sep='_')[0]
        lema_act = lemma_info(act)
        return lema_act

def data_split(hoi):
    hoi = hoi.split(sep='/')
    return hoi[0], hoi[1]

def extra_add_action_and_pair(init, data_dir, resName, hoi_fileName):

    origPhraseAct = load_pickle_object('action_orgPhrase.pkl', compress=False)
    insID = load_pickle_object('instID.pkl', compress=False)
    hoiPair = insID['hoiPairID']
    all_act = load_pickle_object('all_act.pkl', compress=False)
    all_obj = load_pickle_object('all_obj.pkl', compress=False)

    ##############################################################
    # with open(os.path.join(data_dir, hoi_fileName)) as f:
    #     for line in f:
    #         line = line.replace('\n',"")
    #         act, obj = line.split('/')
    extra_hoidata = load_json_object(hoi_fileName + '.json')
    img_id = extra_hoidata.keys()
    for id in img_id:
        img_pair = extra_hoidata[id]
        hois = img_pair['hois']
        for hoi in hois:
            act, obj = hoi.split('/')
            ##############################################################
            obj = obj.capitalize().replace(" ", "_")
            pre_act = preprocessing(act).capitalize()  # ex) talk, kick, work

            hoiAct = HoiAct(act, obj, resName)
            extAct, origPhrase_Act = hoiAct.action_construct(pre_act, origPhraseAct)
            all_concat, all_act, all_obj = hoiAct.all_concat_action_object(pre_act, all_act, all_obj)
            extPair, hoiPair_Dic = HoiPair(act.capitalize(), obj, resName).create_hoiPair(init, hoiPair)

    insID['hoiPairID'].update(hoiPair_Dic)
    dump_pickle_object(origPhrase_Act, 'action_orgPhrase.pkl', compress=False)
    dump_pickle_object(insID, 'instID.pkl', compress=False)
    dump_pickle_object(all_act, 'all_act.pkl', compress=False)
    dump_pickle_object(all_obj, 'all_obj.pkl', compress=False)

    return extAct + all_concat + extPair

def extra_add_action_and_imgInfo(init, resName, img_fileName):

    extra_imgdata = load_json_object(img_fileName +'.json')  # val_vcoco.json load
    img_id = extra_imgdata.keys()

    insID = load_pickle_object('instID.pkl', compress=False)
    hoiPair = insID['hoiPairID']
    imgID = insID['imgID']

    for id in img_id:
        img_pair = extra_imgdata[id]
        file_name = img_pair['file_name']
        hois = img_pair['hois']
        imgSet = ImgsetAdd(init, file_name, None, imgID)
        for hoi in hois:
            hoi_action, hoi_object = data_split(hoi)  # hold_obj suitcase
            hcvrdimg, hoiPair = imgSet.imgConstruct(resName, hoiPair, hoi_action, hoi_object)

    insID['hoiPairID'] = hoiPair
    insID['imgID'] = imgID
    dump_pickle_object(insID, 'instID.pkl', compress=False)

    return hcvrdimg
