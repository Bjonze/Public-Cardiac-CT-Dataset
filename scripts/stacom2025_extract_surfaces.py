import SimpleITK as sitk
import vtk
from vtk.util.numpy_support import vtk_to_numpy
from vtk.util.numpy_support import numpy_to_vtk
from pathlib import Path
import numpy as np


def sitk2vtk(img):
    """Convert a SimpleITK image to a VTK image, via numpy."""
    size = list(img.GetSize())
    origin = list(img.GetOrigin())
    spacing = list(img.GetSpacing())
    ncomp = img.GetNumberOfComponentsPerPixel()
    direction = img.GetDirection()

    # convert the SimpleITK image to a numpy array
    i2 = sitk.GetArrayFromImage(img)
    vtk_image = vtk.vtkImageData()

    # VTK expects 3-dimensional parameters
    if len(size) == 2:
        size.append(1)

    if len(origin) == 2:
        origin.append(0.0)

    if len(spacing) == 2:
        spacing.append(spacing[0])

    if len(direction) == 4:
        direction = [
            direction[0],
            direction[1],
            0.0,
            direction[2],
            direction[3],
            0.0,
            0.0,
            0.0,
            1.0,
        ]

    vtk_image.SetDimensions(size)
    vtk_image.SetSpacing(spacing)
    vtk_image.SetOrigin(origin)
    vtk_image.SetExtent(0, size[0] - 1, 0, size[1] - 1, 0, size[2] - 1)

    vtk_image.SetDirectionMatrix(direction)

    depth_array = numpy_to_vtk(i2.ravel(), deep=True)
    depth_array.SetNumberOfComponents(ncomp)
    vtk_image.GetPointData().SetScalars(depth_array)
    vtk_image.Modified()

    return vtk_image


def convert_label_map_to_surface(label_image_sitk, segment_id=1,
                                only_largest_component=True):
    vtk_img = sitk2vtk(label_image_sitk)

    mc = vtk.vtkDiscreteMarchingCubes()
    mc.SetInputData(vtk_img)
    mc.SetNumberOfContours(1)
    mc.SetValue(0, segment_id)
    mc.Update()

    if mc.GetOutput().GetNumberOfPoints() < 10:
        print(f"No isosurface found for segment {segment_id}")
        return None

    surface = mc.GetOutput()
    if only_largest_component:
        conn = vtk.vtkConnectivityFilter()
        conn.SetInputConnection(mc.GetOutputPort())
        conn.SetExtractionModeToLargestRegion()
        conn.Update()
        surface = conn. GetOutput()
    return surface


def extract_organ_surface_mesh(seg_in, surf_out, organ_id):
    print(f"Reading segmentation {seg_in}")

    try:
        label_img = sitk.ReadImage(seg_in)
    except RuntimeError as e:
        print(f"Got an exception {str(e)}")
        print(f"Error reading {seg_in}")
        return
    print(f"Image size: {label_img.GetSize()}")

    print(f"Extracting and saving surface mesh")
    surface = convert_label_map_to_surface(label_img, segment_id=organ_id, only_largest_component=True)
    if surface is None:
        print(f"No surface extracted for organ {organ_id}")
        return
    writer = vtk.vtkPolyDataWriter()
    writer.SetFileName(surf_out)
    writer.SetInputData(surface)
    writer.Write()
    print(f"Saved surface mesh to {surf_out}")

def extract_all_complete_laa_surfaces():
    label_folder = "C:/data/ImageCAS-STACOM2025-02-10-2025/segmentations/"    
    surface_folder = "C:/data/ImageCAS-STACOM2025-02-10-2025/surfaces/"
    in_files = "C:/data/ImageCAS-STACOM2025-02-10-2025/info/all_full_laa_segmentations_id.txt"
    laa_segm_id = 8

    Path(surface_folder).mkdir(parents=True, exist_ok=True)

    # Read the list of files
    print(f"Reading file list from {in_files}")
    file_list = np.loadtxt(in_files, dtype=str)
    print(f"Found {len(file_list)} files")

    for f in file_list:
        seg_in = f"{label_folder}{f}.nii.gz"
        surf_out = f"{surface_folder}{f}_laa_surface.vtk"
        print(f"Processing {seg_in}")
        extract_organ_surface_mesh(seg_in, surf_out, organ_id=laa_segm_id)

if __name__ == '__main__':
    extract_all_complete_laa_surfaces()
