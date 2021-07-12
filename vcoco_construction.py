#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os.path
import vsrl_utils as vu
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

def vcoco_data_split(hoi):
    hoi = hoi.split(sep='/')
    return hoi[0], hoi[1]

def vcoco_create_action_and_pair(init, resName, name, all_obj):

    origPhraseAct = {}                          ## Dictionary of 'base form - phrase' relationships in Action   ex) Hit : ['Hit_instr', 'Hit_obj']
    hoiPair = {}                                ## Dictionary for hoi Pair    ex) 000001_Stand : [] // 000002_Sit_instr : Bicycle
    all_act = {}

    vcoco_all = vu.load_vcoco('vcoco_' + name)
    action_name = [x['action_name'] for x in vcoco_all]
    role_name = [x['role_name'][1:] for x in vcoco_all]
    object_include = [x['include'][1:] for x in vcoco_all]

    #### V-COCO - Property extract and connect  ####
    # actionId :  0번 hold
    # roleName :  obj
    # roleObj  :  []
    for actName in action_name:
        # print("actName : ", actName)
        actionId = action_name.index(actName)
        roleName = role_name[actionId]
        roleObj = object_include[actionId]

        pre_action = preprocessing(actName).capitalize()                        # ex) talk, kick, work

        ## If role_name does not exist ex) Stand, Walk, Run
        if len(roleName) == 0:
            hoiAct = HoiAct(actName, roleObj, resName)
            vcocoAct, origPhrase_Act = hoiAct.action_construct(pre_action, origPhraseAct)
            all_concat, all_act, all_obj = hoiAct.all_concat_action_object(pre_action, all_act, all_obj)
            vcocoPair, hoiPair_Dic = HoiPair(actName.capitalize(), roleObj, resName).create_hoiPair(init, hoiPair)

        ## If role_name is 1 ex) Hold, Sit, Ride
        elif len(roleName) == 1 :
            if not roleObj[0] :
                hoiAct = HoiAct(actName, roleObj[0], resName)
                vcocoAct, origPhrase_Act = hoiAct.action_construct(pre_action, origPhraseAct)
                all_concat, all_act, all_obj = hoiAct.all_concat_action_object(pre_action, all_act, all_obj)
                vcocoPair, hoiPair_Dic = HoiPair(actName.capitalize(), roleObj[0], resName).create_hoiPair(init, hoiPair)
            else :
                obj = [x.capitalize().replace(" ", "_") for x in roleObj[0]]
                for key, obj in enumerate(obj):
                    hoiAct = HoiAct(actName, obj, resName)
                    vcocoAct, origPhrase_Act = hoiAct.action_construct(pre_action, origPhraseAct)
                    all_concat, all_act, all_obj = hoiAct.all_concat_action_object(pre_action, all_act, all_obj)
                    vcocoPair, hoiPair_Dic = HoiPair(actName.capitalize(), obj, resName).create_hoiPair(init, hoiPair)
                    #print(roleObj[0])
        else:
            ## Connect the object matching role_name
            for i, role in enumerate(roleName):
                action = "{}_".format(actName) + "{}".format(role)              # action_role (hold_obj)
                obj = [x.capitalize().replace(" ", "_") for x in roleObj[i]]
                #print(obj)

                if not obj:
                    hoiAct = HoiAct(action, obj, resName)
                    vcocoAct, origPhrase_Act = hoiAct.action_construct(pre_action, origPhraseAct)
                    all_concat, all_act, all_obj = hoiAct.all_concat_action_object(pre_action, all_act, all_obj)
                    vcocoPair, hoiPair_Dic = HoiPair(action.capitalize(), obj, resName).create_hoiPair(init, hoiPair)
                else:
                    for key, obj in enumerate(obj):
                        hoiAct = HoiAct(action, obj, resName)
                        vcocoAct, origPhrase_Act = hoiAct.action_construct(pre_action, origPhraseAct)
                        all_concat, all_act, all_obj = hoiAct.all_concat_action_object(pre_action, all_act, all_obj)
                        vcocoPair, hoiPair_Dic = HoiPair(action.capitalize(), obj, resName).create_hoiPair(init, hoiPair)


    dump_pickle_object(origPhrase_Act, 'action_orgPhrase.pkl', compress=False)
    dump_pickle_object(hoiPair_Dic, 'instID.pkl', compress=False)
    dump_pickle_object(all_act, 'all_act.pkl', compress=False)
    dump_pickle_object(all_obj, 'all_obj.pkl', compress=False)
    return vcocoAct + all_concat + vcocoPair

def vcoco_add_action_and_imgInfo(init, resName):

    vcoco_data = load_json_object('trainval_vcoco.json')
    img_id = vcoco_data.keys()

    hoiPair = load_pickle_object('instID.pkl',compress=False)
    imgID = []

    for id in img_id:
        img_pair = vcoco_data[id]
        file_name = img_pair['file_name']
        coco_url = img_pair['coco_url']
        hois = img_pair['hois']
        imgSet = ImgsetAdd(init, file_name, coco_url, imgID)
        for hoi in hois:
            hoi_action, hoi_object = vcoco_data_split(hoi)  # hold_obj suitcase
            vcocoimg, hoiPair = imgSet.imgConstruct(resName, hoiPair, hoi_action, hoi_object)

    # for key, val in hoiPair.items():
    #     print("{key} : {value}".format(key=key, value=val))
    instID = {
        'hoiPairID' : hoiPair,
        'imgID': imgID
    }

    dump_pickle_object(instID, 'instID.pkl', compress=False)

    return vcocoimg


