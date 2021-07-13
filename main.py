import os
import json
import argparse
from rdflib import Graph

from io_utils import removeExtensionFile
from create_hoiOnto import create_initial_hoiOnto, hico_dataset_expansion, extra_dataset_expansion
from create_addset import create_hoiOnto_addset

parser = argparse.ArgumentParser()
parser.add_argument('-ci', '--create_initial_hoiOnto', default='f', type=str,                   ## t(true) or f(false)
                    help="If the initial hoiOnto does not exist, create it")
parser.add_argument('-hd_ep', '--hico_data_expansion', default='f', type=str,                   ## t(true) or f(false)
                    help="If you want to expand the hico dataset, try it")

# other dataset parameters
parser.add_argument('-ext_ep', '--extra_dataset_expansion', default='f', type=str,              ## t(true) or f(false)
                    help="If you want to expand the other dataset, try it")
parser.add_argument('-ext_rn', '--extra_dataset_resource_name', type=str,                      
                    help="The name of the data resource to expand (Added to 'InteractionSource class' instance)")
parser.add_argument('-ext_hoi', '--extra_dataset_hoiPair', type=str,                         
                    help="The name of the HOI Pair data file")
parser.add_argument('-ext_img', '--extra_dataset_img', type=str,                               
                    help="The name of the Image information data file")

# file name parameters
parser.add_argument('-ro', '--read_onto_file_name', type=str,                                   
                    help="Ontology file name to be expanded")
parser.add_argument('-sa_eo', '--save_exp_onto_file_name', default='exp_hoiOnto', type=str,     
                    help="The newly expanded hoiOnto name in which you want to save")

# addset parameters
parser.add_argument('-addset', '--create_hoiOnto_addset',type=str,
                    help="Create an addset for the task you want to use")
parser.add_argument('-sa_ad', '--save_addset_file_name', default='hoiOnto_addset', type=str,
                    help="The addset name in which you want to save")


args = parser.parse_args()

create_initial = args.create_initial_hoiOnto
hico_expansion = args.hico_data_expansion

extDa_expansion = args.extra_dataset_expansion
extDa_resName = args.extra_dataset_resource_name
extDa_hoi = args.extra_dataset_hoiPair
extDa_img = args.extra_dataset_img

onto_file_name = args.read_onto_file_name
save_ontoN = args.save_exp_onto_file_name

addset = args.create_hoiOnto_addset
save_addset = args.save_addset_file_name


with open('infos/directory.json') as fp : data_dir = json.load(fp)
storage_dir = data_dir + 'storage'
if not os.path.isdir(storage_dir):
    os.mkdir(storage_dir)

if __name__ == '__main__':

    if create_initial == 't':
        removeExtensionFile(storage_dir, '.pkl')
        create_initial_hoiOnto(create_initial, data_dir)

    if hico_expansion == 't':
        g = Graph()
        previous_onto = g.parse(data_dir + onto_file_name)
        hico_dataset_expansion(create_initial, previous_onto, data_dir)

    ## Extra Dataset
    if extDa_expansion == 't' :
        g = Graph()
        previous_onto = g.parse(data_dir + onto_file_name)
        extra_dataset_expansion(create_initial,previous_onto, data_dir, extDa_resName, extDa_hoi, extDa_img, save_ontoN)

    ## Create hoiOnto addset
    if addset :
        create_hoiOnto_addset(addset, save_addset)
