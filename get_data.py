import os
import vsrl_utils as vu
import numpy as np
import json

from scipy.io import loadmat
from pycocotools.coco import COCO

with open('infos/directory.json', 'r') as fp : data_dir = json.load(fp)

coco = COCO(os.path.join(data_dir, 'coco/instances_trainval2017.json'))

VERB2ID = ['carry', 'catch', 'cut', 'drink', 'eat', 'hit','hold', 'jump', 'kick', 'lay', 'look', 'point', 'read', 'ride', 'run', 'sit', 'skateboard', 'ski', 'smile',
           'snowboard', 'stand', 'surf', 'talk_on_phone', 'throw', 'walk', 'work_on_computer']

def create_dict(data_dict, image_id, file_name, coco_url, hois):

    d = data_dict.get(image_id, {})

    if not d:
        d['file_name'] = file_name
        d['coco_url'] = coco_url
        d['hois'] = [hois]
    elif not d.get('hois', {}):
        d['hois'].append(hois)
    elif not hois in d.get('hois', {}):
        d['hois'].append(hois)

    return d

def get_vcoco_data(name, data_dict):

    vcoco_all = vu.load_vcoco('vcoco_' + name)

    # Action classes and roles in V-COCO
    classes = [x['action_name'] for x in vcoco_all]
    role_name = [x['role_name'] for x in vcoco_all]

    for act in VERB2ID :  # len=26
        cls_id = classes.index(act)
        vcoco = vcoco_all[cls_id]
        roleName = role_name[cls_id]

        np.random.seed(1)
        positive_index = np.where(vcoco['label'] == 1)[0]
        positive_index = np.random.permutation(positive_index)

        for i in range(len(positive_index)):
            id = positive_index[i]
            image_id = str(vcoco['image_id'][id][0])

            # load image
            coco_image = coco.loadImgs(ids=[vcoco['image_id'][id][0]])[0]
            coco_url = str(coco_image['coco_url'])
            file_name = str(coco_image['file_name'])

            role_obj = vcoco['role_object_id'][id]
            if len(vcoco['role_name']) == 1 :               # run, smile, stand, walk
                hois = act + "/" + '[]'
                d = create_dict(data_dict, image_id, file_name, coco_url, hois)
                data_dict[image_id] = d
            elif len(vcoco['role_name']) == 2 :
                for j in range(1, len(vcoco['role_name'])):
                    if not role_obj[j] == 0:
                        anns = coco.loadAnns(ids=[role_obj[j]])
                        categories = coco.loadCats(anns[0]['category_id'])
                        hois = act + "/" + categories[0]['name'].replace(" ", "_")
                    else :
                        hois = act + "/" + '[]'

                    d = create_dict(data_dict, image_id, file_name, coco_url, hois)
                    data_dict[image_id] = d

            else :
                for j in range(1, len(vcoco['role_name'])) :
                    if not role_obj[j] == 0:
                        anns = coco.loadAnns(ids=[role_obj[j]])
                        categories = coco.loadCats(anns[0]['category_id'])
                        hois = act + "_" + roleName[j] + "/" + categories[0]['name'].replace(" ", "_")
                    else:
                        hois = act + "_" + roleName[j] + "/" + '[]'

                    d = create_dict(data_dict, image_id, file_name, coco_url, hois)
                    data_dict[image_id] = d

    return data_dict

def get_hico_data(data_dict, data_dir, set):

    mat_data_anno = loadmat(data_dir + "hico/anno.mat")
    mat_data_annoBox = loadmat(data_dir + "hico/anno_bbox.mat")

    annoBox_value = mat_data_annoBox.get('bbox_' + set)[0]
    hico_list_action = mat_data_anno['list_action']

    for anno in annoBox_value:
        for anno_hoi in anno['hoi']['id']:
            for hoi in anno_hoi:

                file_name = anno['filename'][0]
                fName = file_name.split(sep='.')
                data, data_set, image_id = fName[0].split(sep='_')

                hoi_id = hoi[0][0]
                hoi_list = hico_list_action[hoi_id - 1][0]

                obj_name = hoi_list[0][0].replace(" ", "_")
                action_name = hoi_list[1][0].replace(" ", "_")

                hois = action_name + "/" + obj_name
                d = data_dict.get(image_id, {})

                if not d:
                    d['file_name'] = file_name
                    d['hois'] = [hois]
                elif not d.get('hois', {}):
                    d['hois'].append(hois)
                elif not hois in d.get('hois', {}):
                    d['hois'].append(hois)

                data_dict[image_id] = d

    return data_dict