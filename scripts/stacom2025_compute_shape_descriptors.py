import SimpleITK as sitk
import vtk
from vtk.util.numpy_support import vtk_to_numpy
from vtk.util.numpy_support import numpy_to_vtk
from pathlib import Path
import numpy as np
import multiprocessing as mp
import json
from sklearn.decomposition import PCA
import os
import json
import csv


def shape_pca_analysis(laa_pd, result_dict):
    """
    https://examples.vtk.org/site/PythonicAPI/Utilities/PCADemo/
    https://pyradiomics.readthedocs.io/en/latest/features.html#radiomics.shape.RadiomicsShape.getMajorAxisLengthFeatureValue
    """
    print(f"LAA PCA analysis")
    n_samples = laa_pd.GetNumberOfPoints()
    n_features = 3

    # print(f"Creating date matrix of size {n_samples} x {n_features}")
    data_matrix = np.zeros((n_samples, n_features))
    for i in range(0, laa_pd.GetNumberOfPoints()):
        p = laa_pd.GetPoint(i)
        data_matrix[i, 0] = p[0]
        data_matrix[i, 1] = p[1]
        data_matrix[i, 2] = p[2]

    # mean_point = np.mean(data_matrix, axis=0)

    # print(f"Doing PCA")
    shape_pca = PCA()

    # Get eigenvalues and eigenvectors
    shape_pca.fit(data_matrix)
    eigenvalues = shape_pca.explained_variance_
    # eigenvectors = shape_pca.components_

    # print(f"Eigenvalues: {eigenvalues}")
    major_axis_length = 4 * np.sqrt(eigenvalues[0])
    minor_axis_length = 4 * np.sqrt(eigenvalues[1])
    least_axis_length = 4 * np.sqrt(eigenvalues[2])
    elongation = minor_axis_length / major_axis_length
    flatness = least_axis_length / major_axis_length

    result_dict['major_axis_length'] = major_axis_length
    result_dict['minor_axis_length'] = minor_axis_length
    result_dict['least_axis_length'] = least_axis_length
    result_dict['elongation'] = elongation
    result_dict['flatness'] = flatness


def compute_mass_properties(laa_pd, result_dict):
    """
    Alyassin A.M. et al, "Evaluation of new algorithms for the interactive measurement of surface area and volume", Med Phys 21(6) 1994.
    """
    mass_properties = vtk.vtkMassProperties()
    mass_properties.SetInputData(laa_pd)
    mass_properties.Update()

    volume = mass_properties.GetVolume()
    surface_area = mass_properties.GetSurfaceArea()

    # This characterizes the deviation of the shape of an object from a sphere. A sphere's NSI is one. This number is always >= 1.0.
    nsi = mass_properties.GetNormalizedShapeIndex()
    surface_to_volume_ratio = surface_area / volume

    result_dict['volume'] = volume
    result_dict['surface_area'] = surface_area
    result_dict['normalized_shape_index'] = nsi
    result_dict['surface_to_volume_ratio'] = surface_to_volume_ratio
    return True



def analyze_one_scan(surface_folder, descriptor_folder, scan_id):
    result_dict = {}

    laa_surface = f"{surface_folder}{scan_id}_laa_surface.vtk"
    descriptors_out = f"{descriptor_folder}{scan_id}_shape_descriptors.json"

    laa_pd_read = vtk.vtkPolyDataReader()
    laa_pd_read.SetFileName(laa_surface)
    laa_pd_read.Update()
    laa_pd = laa_pd_read.GetOutput()

    compute_mass_properties(laa_pd, result_dict)
    shape_pca_analysis(laa_pd, result_dict)
    with open(descriptors_out, 'w') as f:
        json.dump(result_dict, f, indent=4)
    print(f"Saved descriptors to {descriptors_out}")


def analyzer_process(surface_folder, descriptor_folder, process_queue, process_id):
    while not process_queue.empty():
        scan_id = process_queue.get()
        print(f"Process {process_id} analyzing {scan_id}")
        analyze_one_scan(surface_folder, descriptor_folder, scan_id)

def combine_all_shape_descriptors(descriptor_folder):
    output_csv = f"{descriptor_folder}combined_shape_descriptors.csv"
    print(f"Combining all shape descriptors into {output_csv}")

    # Get list of JSON files
    json_files = [f for f in os.listdir(descriptor_folder) if f.endswith(".json")]

    # Read the first JSON file to get field names
    first_file_path = os.path.join(descriptor_folder, json_files[0])
    with open(first_file_path, 'r') as f:
        first_data = json.load(f)

    # Prepare fieldnames with 'filename' as the first column
    fieldnames = ['filename'] + list(first_data.keys())

    with open(output_csv, mode='w', newline='') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()

        for filename in json_files:
            file_path = os.path.join(descriptor_folder, filename)
            with open(file_path, 'r') as f:
                data = json.load(f)
                data['filename'] = filename.replace("_shape_descriptors.json", "")
                writer.writerow(data)


def compute_all_shape_descriptors():
    surface_folder = "C:/data/ImageCAS-STACOM2025-02-10-2025/surfaces/"
    descriptor_folder = "C:/data/ImageCAS-STACOM2025-02-10-2025/descriptors/"

    Path(descriptor_folder).mkdir(parents=True, exist_ok=True)

    # Get the file list using glob
    file_list = Path(surface_folder).glob("*_laa_surface.vtk")
    # strip path and "_la_surface.vtk" suffix
    file_list = [f.stem.replace("_laa_surface", "") for f in file_list]
    print(f"Found {len(file_list)} surface files")

    process_queue = mp.Queue()
    for idx in file_list:
        scan_id = idx.strip()
        process_queue.put(scan_id)

    # num_processes = mp.cpu_count() - 1
    num_processes = int(mp.cpu_count() / 2)
    print(f"Starting {num_processes} processes")

    processes = []
    for i in range(num_processes):
        p = mp.Process(target=analyzer_process, args=(surface_folder, descriptor_folder, process_queue, i + 1))
        p.start()
        processes.append(p)

    print("Waiting for processes to finish")
    for p in processes:
        p.join()

    combine_all_shape_descriptors(descriptor_folder)



if __name__ == '__main__':
    compute_all_shape_descriptors()
