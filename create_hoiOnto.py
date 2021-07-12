import os
import json
from pycocotools.coco import COCO
from io_utils import dump_json_object, dump_pickle_object
from graph_utils import init_schema, HoiCategory
from get_data import get_vcoco_data, get_hico_data
from vcoco_construction import vcoco_create_action_and_pair, vcoco_add_action_and_imgInfo
from hico_construction import hico_create_action_and_pair, hico_add_action_and_imgInfo
from extra_construction import extra_add_action_and_pair, extra_add_action_and_imgInfo

classes = ["InteractionPairs", "InteractionSource", "Action", "Object", 'ObjectSuperCategory', 'Image']
object_property = ["actionPhrase", "originalForm", "hasAction", "hasObject", "definedBy",
                      "isPairWithObject", "isPairWithAction", "hasSuperCategory", 'hasPair']
data_property = ["hoiID", "fileName", "imageURL", "hasCompression"]

with open('infos/directory.json') as fp : data_dir = json.load(fp)
coco = COCO(os.path.join(data_dir, 'coco_annotations/instances_trainval2017.json'))

def get_all(data_name):
    vcoco_data_dict = {}
    hico_data_dict = {}
    if data_name == 'train_vcoco':
        vcoco_data_dict = get_vcoco_data("train", vcoco_data_dict)
        dump_json_object(vcoco_data_dict, 'train_vcoco.json')
    elif data_name == 'val_vcoco':
        vcoco_data_dict = get_vcoco_data("val", vcoco_data_dict)
        dump_json_object(vcoco_data_dict, 'val_vcoco.json')
    elif data_name == 'trainval_vcoco':
        vcoco_data_dict = get_vcoco_data("trainval", vcoco_data_dict)
        dump_json_object(vcoco_data_dict, 'trainval_vcoco.json')
    elif data_name == 'test_vcoco':
        vcoco_data_dict = get_vcoco_data("test", vcoco_data_dict)
        dump_json_object(vcoco_data_dict, 'test_vcoco.json')
    elif data_name == 'train_hico' :
        hico_data_dict = get_hico_data(hico_data_dict, data_dir, "train")
        dump_json_object(hico_data_dict, 'train_hico.json')
    elif data_name == 'test_hico' :
        hico_data_dict = get_hico_data(hico_data_dict, data_dir, "test")
        dump_json_object(hico_data_dict, 'test_hico.json')


def create_initial_hoiOnto(init, data_dir):

    """
    :param save_folder: Name of the folder which you want to save

    You can choose the ontology format you want to save
    Choose between owl, rdf, and ttl by removing the comments.
    """
    obj_Dic = {}

    categories = coco.loadCats(coco.getCatIds())

    if not os.path.isfile(data_dir + 'trainval_vcoco.json'):
        get_all('trainval_vcoco')

    init_graph = init_schema(classes, object_property, data_property)

    # COCO - Category Create
    for category in categories:
        superCat = category['supercategory']
        objectCat = category['name']
        const_class, all_obj = HoiCategory(superCat, objectCat).categoryConstruct(obj_Dic)

    # V-COCO - Action, HOI Pair Create
    vcoco_pair = vcoco_create_action_and_pair(init, 'vcoco', "trainval", all_obj)
    vcoco_img = vcoco_add_action_and_imgInfo(init, 'vcoco')

    hoiOnto = init_graph + const_class + vcoco_pair + vcoco_img

    hoiOnto.serialize(data_dir + "initial_hoiOnto.owl", format="pretty-xml")
    # hoiOnto.serialize(data_dir + "initial_hoiOnto.rdf", format="pretty-xml")
    # hoiOnto.serialize(data_dir + "initial_hoiOnto.ttl", format="turtle")


def hico_dataset_expansion(init, previous_onto, data_dir):

    if not os.path.isfile(data_dir + 'train_hico.json'):
        get_all('train_hico')

    ## HICO - Action, HOI Pair, Image Create
    extra_pair = hico_create_action_and_pair(init, data_dir, 'hico', "hico_list_hoi.txt")
    extra_img = hico_add_action_and_imgInfo(init, 'hico')

    ext_onto = extra_pair + extra_img

    exp_hoiOnto = previous_onto + ext_onto
    exp_hoiOnto.serialize(data_dir + "exp_hico_hoiOnto.owl", format="pretty-xml")
    # exp_hoiOnto.serialize(data_dir + "exp_hico_hoiOnto.rdf", format="pretty-xml")
    # exp_hoiOnto.serialize(data_dir + "exp_hico_hoiOnto.ttl", format="turtle")


def extra_dataset_expansion(init, previous_onto, data_dir, resName, extDa_hoi, extDa_img, save_ontoName):

    ## Extra Dataset - Action, HOI Pair, Image Create
    if not extDa_img :
        extra_pair = extra_add_action_and_pair(init, data_dir, resName, extDa_hoi)
        ext_onto = extra_pair
    else:
        extra_pair = extra_add_action_and_pair(init, data_dir, resName, extDa_img)
        extra_img = extra_add_action_and_imgInfo(init, resName, extDa_img)
        ext_onto = extra_pair + extra_img

    exp_hoiOnto = previous_onto + ext_onto
    exp_hoiOnto.serialize(data_dir + save_ontoName + ".owl", format="pretty-xml")
    # exp_hoiOnto.serialize(data_dir + save_ontoName + ".rdf", format="pretty-xml")
    # exp_hoiOnto.serialize(data_dir + save_ontoName + ".ttl", format="turtle")