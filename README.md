# hoiOnto
This project is a HOI ontology construction project that can be utilized in the HOI research field. HOI Ontology supports interoperability of different HOI Datasets. In addition, user-based information retrieval is possible through queries, and create an integrated dataset that can be used additionally. More information on how to use it can be found [here](https://drive.google.com/drive/folders/1J8mN63bNIrTdBQzq7Lpjp4qxMXgYI-yF?usp=sharing).

## Install and Download
### 1. Clone:
```Shell
git clone --recursive https://github.com/aryoungkim/hoiOnto.git
```
### 2. Dataset
To create an HOI ontology, To create a hoiOnto addset, we use the annotation files provided by the VSGNet authors. The annotation files can be downloaded from [here](https://drive.google.com/open?id=1WI-gsNLS-t0Kh8TVki1wXqc3y2Ow1f2R). The downloaded annotation files have to be placed as follows.

#### HICO-DET
HICO-DET dataset can be downloaded [here](https://drive.google.com/open?id=1QZcJmGVlF9f4h-XLWe9Gkmnmj2z1gSnk). After finishing downloading, unzip the (`hico_20160224_det.tar.gz`), and then place the annotation files as follows.

```
hoiOnto
 |─ data
 │   └─ hico
 |       |─ anno.mat
 |       |─ anno_bbox.mat
 |       |─ hico_list_hoi.txt
 |       |─ hico_list_obj.txt
 :       :
 |       |─ annotations
 |       |   |─ trainval_hico.json
 |       |   |─ test_hico.json
 |       |   └─ corre_hico.npy
 :       :
```

#### V-COCO
First clone the repository of V-COCO from [here](https://github.com/s-gupta/v-coco), and then follow the instruction to generate the file `instances_vcoco_all_2014.json`. Next, download the prior file `prior.pickle` from [here](https://drive.google.com/drive/folders/10uuzvMUCVVv95-xAZg5KS94QXm7QXZW4). Place the files and make directories as follows.
```
hoiOnto
 |─ data
 │   └─ vcoco
 |       |─ instances_vcoco_all_2017.json
 |       |─ vcoco_test.json
 |       |─ vcoco_train.json
 |       |─ annotations
 :       :
```
For our implementation, the annotation file have to be converted to the HOIA format. The conversion can be conducted as follows.
```
hoiOnto
 |─ data
 │   └─ vcoco
 |       |─ instances_vcoco_all_2017.json
 |       |   |─ instances_vcoco_all_2014.json
 |       |   :
 |       |─ prior.pickle
 |       |─ images
 |       |   |─ train2014
 |       |   |   |─ COCO_train2014_000000000009.jpg
 |       |   |   :
 |       |   └─ val2014
 |       |       |─ COCO_val2014_000000000042.jpg
 |       |       :
 |       |─ annotations
 :       :
```
