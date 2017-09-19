import os

from .load_ct import read_dicom_files


def crop_dicom(path_to_dicom, begin, end, output=None):
    """
    This function crops a dicom series in the x-, y- and z-dimension. If an output path is provided, it will save the
    new series at that location.

    Examples for how to specify cropping mask using the begin- and end-parameter:

        The given DICOM series contains images with the resolution of 512x512 pixels and 133 images
        starting at a depth of -10 mm to a depth of -340 mm. Using begin = [0, 0, -10] and end = [512, 512, -340] would
        give you back the full series. Using begin = [100, 200, -160] and end = [120, 220, -170] would give you a
        new series with 5 images of size 20x20 pixels.

    Args:
        path_to_dicom: String containing the path containing the DICOM-series
        begin: List containing three numbers representing the starting point for cropping. See examples above.
        end: List containing three numbers representing the starting point for cropping. See examples above.
        output: (optional) String containg the path to where to save the cropped series.

    Returns:
        A list of pydicom Dataset-objects representing the cropped series.

    """

    cropped_series = []
    files = read_dicom_files(path_to_dicom + '/*.dcm')

    if output and not os.path.exists(output):
        os.makedirs(output)

    new_dim_xy = [end[0] - begin[0], end[1] - begin[1]]
    upper_z = begin[2] if begin[2] > end[2] else end[2]
    lower_z = begin[2] if begin[2] < end[2] else end[2]

    for file in files:
        if file.SliceLocation > upper_z or file.SliceLocation < lower_z:
            continue
        new_file = file
        new_file.PixelData = new_file.pixel_array[begin[0]:end[0], begin[1]:end[1]].tostring()
        new_file.Rows = new_dim_xy[0]
        new_file.Columns = new_dim_xy[1]
        cropped_series.append(new_file)
        if output:
            new_file.save_as(output + "/" + str(new_file.SliceLocation) + ".dcm")

    return cropped_series
