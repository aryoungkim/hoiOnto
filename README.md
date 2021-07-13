# hoiOnto
This project is a HOI ontology construction project that can be utilized in the HOI research field. HOI Ontology supports interoperability of different HOI Datasets. In addition, user-based information retrieval is possible through queries, and create integrated datasets that can be used additionally. More information on how to use it can be found [here](https://drive.google.com/drive/folders/1J8mN63bNIrTdBQzq7Lpjp4qxMXgYI-yF?usp=sharing).

## Download
### 1. Clone:
```Shell
git clone --recursive https://github.com/aryoungkim/hoiOnto.git
```
### 2. Dataset
We generated the HOI ontology using the HOI datasets. As one of HOI ontology use cases, we created a hoiOnto addset from the HOI ontology and applied it to VSGNet. The hoiOnto addset was created using the annotation file provided by the VSGNet authors.

First to create an HOI ontology, download the COCO, V-COCO, HICO-Det datasets (require only annotation files). 
- COCO dataset can be downloaded [here](https://cocodataset.org/#download) 'annotations_trainval2017.zip'. 
- Clone the repository of V-COCO from [here](https://github.com/s-gupta/v-coco), and then follow the instruction to generate the file `instances_vcoco_all_2017.json`. 
- HICO-DET dataset can be downloaded [here](https://drive.google.com/open?id=1QZcJmGVlF9f4h-XLWe9Gkmnmj2z1gSnk). After finishing downloading, unzip the (`hico_20160224_det.tar.gz`). 
- Follow the instruction to download the annotation file provided by the VSGNet. The annotation files can be downloaded from [here](https://github.com/ASMIftekhar/VSGNet). 

The downloaded all annotation files have to be placed as follows.
 
```
hoiOnto
 |─ data
 │   └─ vcoco
 |       |─ instances_vcoco_all_2017.json
 |       |─ vcoco_trainval.json
 |       |─ vcoco_train.json
 :       :
 |       |─ Annotations_vcoco
 |       |   |─ trainval_annotations.json
 |       |   |─ train_annotations.json
 |       |   └─ test_annotations.json
 :       :
 
 │   └─ hico
 |       |─ anno.mat
 |       |─ anno_bbox.mat
 |       |─ hico_list_hoi.txt
 :       :
 |       |─ Annotations_vcoco
 |       |   |─ train_annotations.json
 |       |   └─ test_annotations.json
 :       :
```
