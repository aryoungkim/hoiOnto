import json
import os
import re
import vsrl_utils as vu
import numpy as np

from io_utils import load_json_object, load_pickle_object, dump_json_object
from franz.openrdf.sail.allegrographserver import AllegroGraphServer
from franz.openrdf.repository.repository import Repository
from franz.openrdf.query.query import QueryLanguage

with open('infos/directory.json') as fp: data_dir = json.load(fp)

add_data_dic = {}

AGRAPH_HOST = '168.188.128.191'
AGRAPH_PORT = '10035'
AGRAPH_USER = 'test'
AGRAPH_PASSWORD = '123'

server = AllegroGraphServer(host=AGRAPH_HOST, port=AGRAPH_PORT,
                            user=AGRAPH_USER, password=AGRAPH_PASSWORD)

catalog = server.openCatalog('')
mode = Repository.OPEN
my_repository = catalog.getRepository('hoiOnto_ext', mode)      # repository name
conn = my_repository.getConnection()


vcoco_all = vu.load_vcoco('vcoco_trainval', data_dir)
coco = vu.load_coco(data_dir)
for x in vcoco_all: x = vu.attach_gt_boxes(x, coco)
cats = coco.loadCats(coco.getCatIds())
annotation = coco.loadAnns(coco.getAnnIds())
classes = [x['action_name'] for x in vcoco_all]
role_name = [x['role_name'] for x in vcoco_all]


def data_split(hoi):
    hoi = hoi.split(sep='/')
    return hoi[0], hoi[1]


def clean_up_triple(imgName, act, obj):
    pattern_tag = '<[^>]*>'
    pattern_spc = '[-=+,#/\?:^$.@*\"※~&%ㆍ!』\\‘|\(\)\[\]\<\>`\'…》]'

    img = re.sub(pattern=pattern_tag, repl='', string=str(imgName))
    imgNam = re.sub(pattern=pattern_spc, repl='', string=img)

    act = re.sub(pattern=pattern_spc, repl='', string=str(act).rstrip('en'))
    obj = re.sub(pattern=pattern_spc, repl='', string=str(obj).rstrip('en'))

    return imgNam, act.lower().replace(" ", "_"), obj.lower().replace(" ", "_")


def get_index(imgName, action, object, hbox, obox):

    d = add_data_dic.get(imgName, {})

    obx = dict()
    perx = dict()

    obx['obj_bbx'] = obox
    obx['obj_name'] = object

    perx['person_bbx'] = hbox
    perx['Verbs'] = action
    perx['object'] = obx

    if not d:
        add_data_dic.update({imgName: [perx]})
    elif not add_data_dic.get(imgName):
        add_data_dic[imgName] = [perx]
    elif not perx in add_data_dic.get(imgName):
        add_data_dic[imgName].append(perx)


def get_pair_hoiOnto(filter_data, act, obj):
    act = act.capitalize()
    obj = obj.capitalize()

    sparql_vcoco = ("""
    SELECT Distinct ?fileName ?pairs ?action ?object
    WHERE {
    ?hoiPair a hoiOnto:InteractionPairs;
             hoiOnto:hasAction ?act;
             hoiOnto:hasObject ?obj.
    ?act rdfs:label ?act_label.
    ?obj rdfs:label ?obj_label.
    FILTER ((str(?act_label) = '%s')&& (str(?obj_label) = '%s'))
    {?image hoiOnto:hasPair ?hoiPair.}
    union
    {?hoiPair owl:sameAs ?pair.
    ?image hoiOnto:hasPair ?pair.
    ?pair hoiOnto:hasAction ?acts.
    ?pair hoiOnto:hasObject ?objs.
    ?acts rdfs:label ?act_labels.
    ?objs rdfs:label ?obj_labels.}
    bind(if(bound(?pair), ?pair, ?hoiPair) as ?pairs)
    bind(if(bound(?act_labels), ?act_labels, ?act_label) as ?action)
    bind(if(bound(?obj_labels), ?obj_labels, ?obj_label) as ?object)
    ?image hoiOnto:fileName ?fileName.
    ?image hoiOnto:imageURL ?url.
    FILTER(!regex(STR(?url),'%s'))
    }
    """) % (act.replace("_", " "), obj.replace("_", " "), filter_data)

    sparql_hico = ("""
        SELECT Distinct ?fileName ?pairs ?action ?object
        WHERE {
        ?hoiPair a hoiOnto:InteractionPairs;
                 hoiOnto:hasAction ?act;
                 hoiOnto:hasObject ?obj.
        ?act rdfs:label ?act_label.
        ?obj rdfs:label ?obj_label.
        FILTER ((str(?act_label) = '%s')&& (str(?obj_label) = '%s'))
        {?image hoiOnto:hasPair ?hoiPair.}
        union
        {?hoiPair owl:sameAs ?pair.
        ?image hoiOnto:hasPair ?pair.
        ?pair hoiOnto:hasAction ?acts.
        ?pair hoiOnto:hasObject ?objs.
        ?acts rdfs:label ?act_labels.
        ?objs rdfs:label ?obj_labels.}
        bind(if(bound(?pair), ?pair, ?hoiPair) as ?pairs)
        bind(if(bound(?act_labels), ?act_labels, ?act_label) as ?action)
        bind(if(bound(?obj_labels), ?obj_labels, ?obj_label) as ?object)
        ?image hoiOnto:fileName ?fileName.
        FILTER(!regex(STR(?fileName),'%s'))
        }
        """) % (act.replace("_", " "), obj.replace("_", " "), filter_data)

    if filter_data == 'coco':
        query = conn.prepareTupleQuery(QueryLanguage.SPARQL, sparql_vcoco)
    elif filter_data == 'HICO':
        query = conn.prepareTupleQuery(QueryLanguage.SPARQL, sparql_hico)

    with query.evaluate() as result:
        imgName_hois = [clean_up_triple(bindings[0], bindings[2], bindings[3]) for bindings in result if
                   bindings[0] is not None]
        if imgName_hois is not None:
            return imgName_hois

def hico_annotation_get(hico_data, img_dic):
    for imgName, hois in img_dic.items():
        imgNum = imgName.split('_')[-1]
        hico_hois = hico_data.get(imgNum)
        for hoi in hois :
            action, object = data_split(hoi) # hold_obj suitcase
            for hico_hoi in hico_hois:
                hico_act = hico_hoi['Verbs']
                hico_obj = hico_hoi['object']['obj_name']
                if action == hico_act and object == hico_obj :
                    #hois = hico_act + "/" + hico_obj
                    pbox = hico_hoi['person_bbx']
                    obox = hico_hoi['object']['obj_bbx']
                    get_index(imgNum, action, object, pbox, obox)


def vcoco_gt_get(action, object, imgName) :
    if action == 'cut_obj' or action == 'cut_instr': action = 'cut'
    elif action == 'hit_obj' or action == 'hit_instr': action = 'hit'
    elif action == 'eat_obj' or action == 'eat_instr': action = 'eat'

    cls_id = classes.index(action)                            # 먼저, action에 대한 index 받고
    vcoco = vcoco_all[cls_id]                                 # action의 정보 불러오기

    gt_obox = []
    img_idx = np.where(vcoco['image_id'] == int(imgName))[0]  # action의 image_id에 add img의 index 찾기, 몇번째에 위치하는지. anntation 번호를 찾을려고 하는거임
    for id in img_idx:
        if vcoco['label'][id][0] == 1:
            role_obj = vcoco['role_object_id'][id]
            role_bbox = vcoco['role_bbox'][id, :] * 1.
            role_bbox = role_bbox.reshape((-1, 4))
            for j in range(1, len(vcoco['role_name'])):
                if not role_obj[j] == 0:
                    obj_anns = coco.loadAnns(ids=[role_obj[j]])
                    obj_categories = coco.loadCats(obj_anns[0]['category_id'])[0]['name']
                    if obj_categories == object.replace("_", " "):
                        if not np.isnan(role_bbox[j, 0]):
                            obox = role_bbox[[j], :][0]
                            if not obox.tolist() in gt_obox :
                                gt_obox.append(obox.tolist())
    return gt_obox


def vcoco_annotation_get(vcoco_data, img_dic):
    vcoco_data_key = [x for x in vcoco_data.keys()]

    for imgName, hois in img_dic.items():
        if str(int(imgName)) in vcoco_data_key :
            vcoco_hois = vcoco_data.get(str(int(imgName)))
            for hoi in hois :
                action, object = data_split(hoi) # hold_obj suitcase
                vcoco_hoi = [hoi for hoi in vcoco_hois if hoi['Verbs'] == action]
                vcoco_obox = [hoi['object']['obj_bbx'] for hoi in vcoco_hois if hoi['Verbs'] == action]

                gt_obox = vcoco_gt_get(action, object, imgName)

                for idx in range(len(vcoco_obox)) :
                    obox = vcoco_obox[idx]
                    hoi = vcoco_hoi[idx]
                    if obox in gt_obox :
                        get_index(int(imgName), action, object, hoi['person_bbx'], obox)


def hoiOnto_addset(filter_data, get_task_data, get_imgid, anno_data, save_fileName):

    img_dic = {}
    pair_dic = {}

    for id in get_imgid:
        img_pair = get_task_data[id]
        hois = img_pair['hois']
        for hoi in hois:
            action, object = data_split(hoi)  # hold_obj suitcase
            if not object == '[]' or action == 'no_interaction':
                if action not in pair_dic.keys():
                    pair_dic.update({action: [object]})
                    imgList_hois = get_pair_hoiOnto(filter_data, action, object)
                if not pair_dic.get(action):
                    pair_dic[action] = [object]
                    imgList_hois = get_pair_hoiOnto(filter_data, action, object)
                elif object not in pair_dic.get(action):
                    pair_dic[action].append(object)
                    imgList_hois = get_pair_hoiOnto(filter_data, action, object)

                if imgList_hois:
                    for imgHois in imgList_hois :
                        pair = imgHois[1] + '/' + imgHois[2]
                        #print(pair)
                        if imgHois[0] not in img_dic.keys():
                            img_dic.update({imgHois[0]: [pair]})
                        if not img_dic.get(imgHois[0]):
                            img_dic[imgHois[0]] = [pair]
                        elif pair not in img_dic.get(imgHois[0]):
                            img_dic[imgHois[0]].append(pair)

    if filter_data == 'coco':
        hico_annotation_get(anno_data, img_dic)
    elif filter_data == 'HICO':
        vcoco_annotation_get(anno_data, img_dic)
    dump_json_object(add_data_dic, save_fileName + '.json')


def create_hoiOnto_addset(addset, save_fileName):

    ## Create hoiOnto addset
    if addset == 'vcoco':
        filter_data = 'coco'
        get_task_data = load_json_object('trainval_vcoco.json')
        get_imgid = [x for x in get_task_data.keys()]
        add_anno_data = load_json_object('hico/train_annotations.json')

    elif addset == 'hico':
        filter_data = 'HICO'
        get_task_data = load_json_object('test_hico.json')
        get_imgid = [x for x in get_task_data.keys()]
        add_anno_data = load_json_object('vcoco/trainval_annotations.json')

    elif addset == 'extra':
        ## Example
        filter_data = ''
        get_task_data = load_json_object('.json')
        get_imgid = [x for x in get_task_data.keys()]
        add_anno_data = load_json_object('.json')

    hoiOnto_addset(filter_data, get_task_data, get_imgid, add_anno_data, save_fileName)