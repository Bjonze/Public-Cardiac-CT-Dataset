# STACOM2025---A-Public-Cardiac-CT-Dataset-Featuring-the-Left-Atrial-Appendage

Official GitHub repo for the article "A Public Cardiac CT Dataset Featuring the Left Atrial Appendage" published at the STACOM 2025 MICCAI workshop. 

## Introduction
This is the data described in the publication (please cite this article if you use the data):

*Bjørn Hansen, Jonas Pedersen, Klaus F. Kofoed, Oscar Camara, Rasmus R. Paulsen and Kristine Sørensen.*
**A Public Cardiac CT Dataset Featuring the Left Atrial Appendage.**
Proceedings STACOM. 
MICCAI workshop on The Statistical Atlases and Computational Modeling of the Heart
Springer 2025

The main page for the dataset is:
https://github.com/Bjonze/Public-Cardiac-CT-Dataset

It contains label maps computed for the public ImageCAS dataset:
- https://www.kaggle.com/datasets/xiaoweixumedicalai/imagecas
- https://github.com/XiaoweiXu/ImageCAS-A-Large-Scale-Dataset-and-Benchmark-for-Coronary-Artery-Segmentation-based-on-CT

## Download the data

The data can be downloaded as a zip file [here](https://people.compute.dtu.dk/rapa/STACOM2025/ImageCAS-STACOM2025-02-10-2025.zip) (576 MB)

## Data description

For each scan, the following labels are computed:

- 0 : **Background**
- 1 : **Myocardium** : The muscle tissue surrounding the left ventricle blood pool
- 2 : **LA** : The left atrium blood pool
- 3 : **LV** : The left ventricle blood pool including the papilary muscles and trabeculation
- 4 : **RA** : The right atrium blood pool
- 5 : **RV** : The right ventricle blood pool
- 6 : **Aorta** : The aorta including the aortic cusp
- 7 : **PA** : The pulmonary artery
- 8 : **LAA** : The left atrial appendage
- 9 : **Coronary** : The left and right coronary arteries
- 10 : **PV** : The pulmonary veins

## Excluded scans
The labelmaps are computed on the entire ImageCAS dataset, but we found that scan 90.img.nii.gz and 141.img.nii.gz are invalid and therefore no labelmaps are computed for them.

## Full and partial left atrial appendages and file lists

For each labelmap it is checked if the left atrial appendage touches the side of the scan due to a limited scan field-of-view. There are two file lists with image ids:

- `all_segmentations_id.txt` : Contains the 998 image ids of the computed label maps
- `all_full_laa_segmentations_id.txt` : Contains the 685 image ids of label maps with complete LAAs (that do not touches the scan side)

## Supplied processing scripts

We supply a set of processing scripts, to easy future use of the data. They are located in the `scripts` sub-folder.

### `stacom2025_extract_surfaces.py`

Extracts the surfaces of all complete left atrial appendages in the dataset. The surfaces are stored as VTK files. To use this script, you should change the folder names in the script to point where you have unpacked the data.

### `stacom2025_compute_shape_descriptors.py`

Computes a set of 3D shape descriptors based on the LAA surfaces extraced using `stacom2025_extract_surfaces.py`. The surface descriptors are currently:

- volume: Volume of the LAA (mm^3)
- surface area: Area of the surface of the LAA (mm^2)
- Normalized shape index as defined in the [VTK documentation](https://vtk.org/doc/nightly/html/classvtkMassProperties.html#details)
- Surface to volume ratio: Surface area divided by the volume
- Major axis length: The length of the first eigenvector computed by doing a PCA on the vertices of the mesh
- Minor axis length: The length of the second eigenvector computed by doing a PCA on the vertices of the mesh
- Least axis length: The length of the third eigenvector computed by doing a PCA on the vertices of the mesh
- [Elongation](https://pyradiomics.readthedocs.io/en/latest/features.html#radiomics.shape.RadiomicsShape.getElongationFeatureValue): The minor axis length divided by the major axis length
- [Flatness](https://pyradiomics.readthedocs.io/en/latest/features.html#radiomics.shape.RadiomicsShape.getFlatnessFeatureValue): The least axis length divided by the major axis length

The computed features are both stored as individual JSON files per scan and as a combined CSV file with all features for all scans.

### `stacom2025_explore_shape_descriptors.py`

Do a simple principal component analysis (PCA) explorative analysis of the computed shapes descriptors from `stacom2025_compute_shape_descriptors.py`.
