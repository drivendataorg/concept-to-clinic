import numpy as np
import scipy.ndimage
import skimage
import skimage.measure
import skimage.filters
import skimage.morphology
import scipy.ndimage.morphology
import skimage.transform
import skimage.segmentation
import itertools

BRONCHIAL_THRESHOLD = -950
INITIAL_THRESHOLD = -950
RADIUS_BALL = 5
MIN_BRONCHIAL_THRESHOLD = -5010
MIN_LUNGS_THRESHOLD = -1040
STEP = 64


def region_growing(img, seed, minthr, maxthr, structure=None):
    """
    Region growing.

    A numpy-style n-dimensional region growing algorithm.
    Code was taken from:
    https://github.com/loli/medpy/wiki/Basic-image-manipulation

    Args:
        img: An image that is a numpy ndarray.
        seed: A seed binary image of the same shape that contains a True-value at each seed point.
        minthr: A minimal threshold value.
        maxthr: A maximum threshold value.
        structure: A structure element that describes the connectedness / neighbourhood

    Returns:
        region: The obtained segmentation region.
    """
    img[seed] = minthr
    thrimg = (img < maxthr) & (img >= minthr)
    lmap, _ = scipy.ndimage.label(thrimg, structure=structure)
    lids = np.unique(lmap[seed])
    region = np.zeros(img.shape, np.bool)
    for lid in lids:
        region |= lmap == lid
    return region


def extract_bronchial(ct_slice, xy_spacing=1.):
    """
    Detection the bronchi and the trachea on CT.

    The bronchi and the trachea have the following properties:
        (1) an average HU below −950,
        (2) a minimum size of 50 mm 2 ,
        (3) a maximum size of 1225 mm 2 ,
        (4) mean x- and y-coordinates not further than 30% of the x- and
        y-dimensions of the image away from the center of the slice.

    Args:
        ct_slice: A label of CT slice.
        xy_spacing (float)

    Returns:
        A label of the segmented bronchi and trachea on CT.
    """
    labeled = skimage.measure.label(ct_slice < BRONCHIAL_THRESHOLD)
    areas = np.bincount(labeled.flatten())
    labels = [i
              for i, area in enumerate(areas)
              if (area * xy_spacing >= 50) and (area * xy_spacing <= 1225)]
    coords = [np.where(labeled == i) for i in labels]

    center = np.array(ct_slice.shape) // 2
    max_dist = np.array(ct_slice.shape) * .3
    labels = [(np.mean(coord, axis=1), label)
              for label, coord in zip(labels, coords)
              if (abs(center - np.mean(coord, axis=1)) < max_dist).all()]

    if len(labels):
        return labeled == min(labels, key=lambda x: sum((x[0] - center) ** 2))[1]

    return None


def select_bronchial(bronchial, ct_slices, levels):
    """
    Selection bronchi.

    Args:
        bronchial: A label of the pixels with the bronchi.
        ct_slices: A label of CT.
        levels: A number of slice with the bronchi.

    Returns:
        bronchial: A label of the pixels with the bronchi.
        ct_slices: A label of CT.
        levels: A number of slice with the bronchi.
    """
    center = np.array(bronchial[0].shape) // 2
    coords = [(np.mean(np.where(bool_slice), axis=1), i)
              for i, bool_slice in enumerate(bronchial)]
    el = min(coords, key=lambda x: sum((x[0] - center) ** 2))
    return bronchial[el[1]], ct_slices[el[1]], levels[el[1]]


def select_seeds(bronchial, ct_clice):
    """
    Selection initial pixel.

    Args:
        bronchial: A label of the pixels with the bronchi.
        ct_clice: A label of CT slice.

    Returns:
        Area of the bronchi with minimal voxels
    """
    return (ct_clice * bronchial) == ct_clice[bronchial].min()


def extract_seeds(patient):
    """
    Extraction initial region.

    Starting at the top, the first 25 slices are examined for
    suitable regions.

    Args:
        patient: A label of CT.

    Returns:
        seeds: A initial region.
    """
    bronchials = list()
    bronch_cts = list()
    levels = list()
    for i in range(25):
        bronchial = extract_bronchial(patient[i])
        if bronchial is not None:
            bronchials.append(bronchial)
            bronch_cts.append(patient[i])
            levels.append(i)

    for i in itertools.chain(range(25), range(-25, 0)):
        bronchial = extract_bronchial(patient[i])
        if bronchial is not None:
            bronchials.append(bronchial)
            bronch_cts.append(patient[i])
            levels.append(i)

    bronchial, ct_slice, level = select_bronchial(bronchials,
                                                  bronch_cts,
                                                  levels)

    seeds = np.zeros(patient.shape)
    seeds[level] = select_seeds(bronchial, ct_slice)

    return seeds


def growing_bronchis(patient, seeds, initial_threshold=INITIAL_THRESHOLD,
                     step=STEP,
                     full_extraction=True):
    """
    Extraction of large airways.

    Before the lungs are segmented, the trachea and
    the bronchi are extracted using the technique of a region growing.
    To initialize the region growing, the start point is automatically
    identified on the upper axial scan slices by searching for related
    areas with the specified properties.
    When an explosion occurred, the increase in threshold was divided by 2.

    Args:
        patient: A label of CT.
        seeds: A initial region (pixel).
        initial_threshold: An average HU.
        step: In each iteration, the threshold was initially increased with 64 HU
        full_extraction: Full extraction of large airways.

    Returns:
        ret: A label of the bronchi at the previous stage.
        seeds: A label of the bronchi.
    """

    seeds = seeds.astype(np.bool_)
    seeds = region_growing(patient.copy(), seeds, MIN_BRONCHIAL_THRESHOLD, initial_threshold)
    volume = np.count_nonzero(seeds)

    lungs_thresh = skimage.filters.threshold_otsu(patient[patient.shape[0] // 2])

    ret = None
    while True:
        labeled = region_growing(patient.copy(), seeds, MIN_BRONCHIAL_THRESHOLD, initial_threshold + step)
        new_volume = np.count_nonzero(labeled)
        if new_volume >= volume * 2:
            if step == 4:
                ret = seeds.copy()
                if not full_extraction:
                    return ret

            if step == 2:
                return ret, seeds
            step = np.ceil(step * 0.5)
            continue

        initial_threshold += step
        volume = new_volume
        seeds = labeled

        if initial_threshold >= lungs_thresh:
            if ret is None:
                ret = seeds.copy()

            if not full_extraction:
                return ret

            return ret, seeds


def grow_lungs(patient, seeds):
    """
    Segmentation of lung regions.

    The lungs are segmented using region growing. As a
    seed point for the region growing, the voxel with the lowest
    HU within the airways is used.

    To determine the upper threshold for the
    region growing operation, optimal thresholding is applied.

    Args:
        patient: a label of CT.
        seeds: a area of trachea

    Returns:
        A label of the segmented lungs.
    """
    lungs_seeds = patient * seeds == patient[seeds].min()
    lungs_seeds = lungs_seeds.astype(np.bool_)
    threshold = skimage.filters.threshold_otsu(patient[patient.shape[0] // 2])
    lungs_seeds = region_growing(patient.copy(), lungs_seeds, MIN_LUNGS_THRESHOLD, threshold)
    return scipy.ndimage.morphology.binary_opening(lungs_seeds - scipy.ndimage.morphology.binary_opening(seeds))


def label_size(labeled_matrix, label):
    return len(labeled_matrix[labeled_matrix == label])


def remove_trash(labeled_matrix, label_num):
    """
    Args:
        labeled_matrix

    Returns:
        int, the amount of colours in the re-labeled array
    """
    skimage.segmentation.clear_border(labeled_matrix)
    max_label_size = 0
    new_label_num = 0
    for i in range(1, label_num + 1):
        if len(labeled_matrix[labeled_matrix == i]) > max_label_size:
            max_label_size = len(labeled_matrix[labeled_matrix == i])

    for i in range(1, label_num + 1):
        if label_size(labeled_matrix, i) < .2 * max_label_size:
            labeled_matrix[labeled_matrix == i] = 0
        else:
            new_label_num += 1
            labeled_matrix[labeled_matrix == i] = new_label_num

    return new_label_num


def if_separate(mask):
    """
    Args:
        mask (np.ndarray[int|bool])

    Returns:
        int, the amount of colours in the re-labeled array
    """
    mask, count = skimage.measure.label(mask, connectivity=1, return_num=True)
    count = remove_trash(mask, count)
    return count != 1


def define_lungs(labeled):
    """
    The left and right lungs are identified by their center of gravity.
    Args:
        labeled np.ndarray[int]

    Returns:
        labeld np.ndarray[int]
    """
    labeld = labeled + 500
    labels = np.bincount(labeld.flatten()).argsort()[-3:-1]
    label0_rightest = np.max(np.where(labeld == labels[0])[1])
    label1_rightest = np.max(np.where(labeld == labels[1])[1])
    if label0_rightest < label1_rightest:
        labeld[labeld == labels[0]] = 1
        labeld[labeld == labels[1]] = 2
    else:
        labeld[labeld == labels[0]] = 2
        labeld[labeld == labels[1]] = 1
    labeld[labeld > 2] = 0
    return labeld


def separate_lungs(label_matrix, layer_num):
    """
    Args:
        label_matrix (np.ndarray[int])
        layer_num

    Returns:
        label_matrix (np.ndarray[int])
    """
    before_morph_open = label_matrix
    while not if_separate(label_matrix):
        label_matrix = scipy.ndimage.morphology.binary_erosion(label_matrix, structure=np.ones((7, 1)))
    label_matrix = skimage.measure.label(label_matrix, connectivity=1)
    inverse_erosion(label_matrix, before_morph_open, layer_num)
    return label_matrix


def inverse_erosion(label_matrix, mask, slice_num):
    """
    Recontruct original morphological shape of `label_matrix`
    by tracing masks of appropriate colours (labels).

    Args:
        label_matrix (np.ndarray[int])
        mask (np.ndarray[int])
        slice_num (int): Number of slice.
    """
    xs, ys = np.where(label_matrix < mask)
    border_coords = list(zip(xs, ys))
    while len(border_coords):
        to1 = []
        to2 = []
        new_border_coords = []
        for x, y in border_coords:
            chunk = label_matrix[x - 1:x + 2, y - 1:y + 2]
            near1 = len(np.where(chunk == 1)[0])
            near2 = len(np.where(chunk == 2)[0])
            if near1 and near2:
                if slice_num % 2:
                    to1.append((x, y))
                else:
                    to2.append((x, y))
            elif near1:
                to1.append((x, y))
            elif len(np.where(chunk == 2)[0]):
                to2.append((x, y))
            else:
                new_border_coords.append((x, y))
        if len(to1) == 0 and len(to2) == 0:
            return
        for x, y in to1:
            label_matrix[x, y] = 1
        for x, y in to2:
            label_matrix[x, y] = 2
        border_coords = new_border_coords


def separate_new_slice(new_slice, prev_slice, slice_num):
    """
    Computes inverse erosion over input data.

    Args:
        new_slice: A transverse slice of segmented lungs.
        prev_slice: A previous transverse slice of segmented lungs.
        slice_num: Number of slice.

    Returns:
        intersect (np.ndarray[int])
    """
    intersect = new_slice * prev_slice
    inverse_erosion(intersect, new_slice, slice_num)
    return intersect


def separate_lungs3d(file_):
    """
    The main idea of the algorithm is to select reference binary image
    of the lungs in a one slice which further will be propagated over
    all adjacent slices, that have not yet been visited, by comparison
    of its complements. This process will be repeated, taking adjacent
    slices from previous step, as new reference images until lungs are
    not separated.

    Args:
        file_: A label of the segmented lungs.

    Returns:
        The masks of segmented and separated lungs.
    """
    interval = np.int(file_.shape[1] * 0.1)
    start_slice_ind = -1
    start_slice = []
    with open('output_nrt', 'w') as f:
        print("finding start slice")
        for i in (range(file_.shape[1] // 2 - interval, file_.shape[1] // 2 + interval)):
            if if_separate(file_[:, i, :]):
                start_slice_ind = i
                break
        f.write(str(start_slice_ind))
        if start_slice_ind == -1:
            start_slice = separate_lungs(file_[:, file_.shape[1] // 2, :], file_.shape[1] // 2)
            start_slice_ind = file_.shape[1] // 2
        else:
            start_slice = define_lungs(skimage.measure.label(file_[:, start_slice_ind, :], connectivity=1))
        cur_slice = start_slice
        ret = file_.astype(int)
        ret[:, start_slice_ind, :] = start_slice
        print("moving forward")
        for i in (range(start_slice_ind + 1, file_.shape[1])):
            new_slice = separate_new_slice(file_[:, i, :].astype(int), cur_slice, i)
            ret[:, i, :] = new_slice
            cur_slice = new_slice
        cur_slice = start_slice
        print("moving backward")
        for i in (range(start_slice_ind - 1, -1, -1)):
            new_slice = separate_new_slice(file_[:, i, :].astype(int), cur_slice, i)
            ret[:, i, :] = new_slice
            cur_slice = new_slice
    return extract_lungs(ret)


def extract_lungs(separated):
    """
    Extract lungs.

    Args:
        separated: A mask of lungs.

    Returns:
        The masks of segmented and separated lungs.
    """
    left_lung = separated.copy()
    left_lung[left_lung != 1] = 0
    right_lung = separated.copy()
    right_lung[right_lung != 2] = 0
    right_lung[right_lung == 2] = 1
    return left_lung, right_lung


def lung_separation(lungs_seeds):
    """
    Lung separation.

    code was taken from:
    https://github.com/vessemer/LungCancerDetection/blob/master/lung_segmentation/lung_separation_frontal.py
    https://github.com/vessemer/LungCancerDetection/blob/master/report.pdf
    Args:
        lungs_seeds: A label of the segmented lungs.

    Returns:
        The two largest areas on CT.
    """
    labeled = skimage.measure.label(lungs_seeds)[0]
    markers = np.bincount(labeled.flatten())
    markers = np.vstack([markers[1:], np.arange(1, markers.shape[0])])
    markers = np.asarray(sorted(markers.T, key=lambda x: x[0]))[-2:]
    if len(markers) < 2:
        left, right = separate_lungs3d(lungs_seeds)
        return left, right, True

    if markers[0, 0] / markers[1, 0] < 0.3:
        left, right = separate_lungs3d(lungs_seeds)
        return left, right, True

    centroids = (np.mean(np.where(labeled == markers[0, 1]), axis=1)[-1],
                 np.mean(np.where(labeled == markers[1, 1]), axis=1)[-1])

    if centroids[0] > centroids[1]:
        return labeled == markers[1, 1], labeled == markers[0, 1], False

    return labeled == markers[0, 1], labeled == markers[1, 1], False


def lungs_postprocessing(lungs_seeds):
    """
    First 3D hole filling is applied
    to include vessels and other high-density structures that were
    excluded by the threshold used in region growing, in the segmentation.

    Next, morphological closing with a spherical
    kernel is applied. The diameter of the kernel is set to 2% of
    the x-dimension of the image.

    Args:
        lungs_seeds: A label with the segmented lungs before postprocessing.

    Returns:
        A label with the segmented lungs after binary_fill_holes.
    """
    for i in range(lungs_seeds.shape[1]):
        lungs_seeds[:, i] = scipy.ndimage.morphology.binary_fill_holes(lungs_seeds[:, i])

    return lungs_seeds


def conventional_lung_segmentation(patient):
    """
    The algorithm consists of the following steps:
        (1)Extraction of large airways;
        (2)Segmentation of lung regions;
        (3)Separation of the left and right lungs;
        (4)Smoothing.

    The function aggregates extract_seeds, growing_bronchis,
    flip_lung, grow_lungs, lungs_postprocessing.

    Args:
        patient: A label of CT.

    Returns:
        lungs_seeds: A label with the segmented lungs.
        left: A label with the segmented left lung.
        right: A label with the segmented right lung.
    """

    seeds = extract_seeds(patient)
    trachea, bronchi = growing_bronchis(patient, seeds)

    lungs_seeds = grow_lungs(patient, trachea)

    selem = skimage.morphology.ball(int(patient.shape[-1] * .01))
    lungs_seeds = skimage.morphology.binary_closing(lungs_seeds, selem)

    lungs_seeds = lungs_postprocessing(lungs_seeds)

    right, left, state = lung_separation(lungs_seeds)

    return right, left, trachea


def cumulation(lung):
    """
    The cumulative x-position inside a lung.

    Args:
        lung: The segmented lung (left or right).

    Returns:
        lung: Cumulative x-position.
        z_coords: z-coordinates in lung.
    """
    z_coords, y_coords, x_coords = np.where(lung)
    current_volume = 0
    volume = np.count_nonzero(lung)
    for coord in np.unique(x_coords):
        current_volume += np.count_nonzero(lung[:, :, coord])
        lung[:, :, coord][lung[:, :, coord] != 0] = current_volume / float(volume)
    return lung, z_coords


def ventricular_extraction(err_lung):
    """
    Extraction of a ventricle.

    On all CT there is a ventricle. In order for the algorithm
    doesn't define the ventricle as a segmentation error,
    it is necessary to remove the error mask of the largest
    size that corresponds to the ventricle.

    Args:
        err_lung: The label of errors in the lung.

    Returns:
        err_lung: The label of errors in the lung without the ventricle.
    """
    max_marker = -1
    z_max = -1
    lav, mar = scipy.ndimage.label(err_lung)
    volumes = np.hstack([np.bincount(lav.flatten()), [-1]])

    for i in range(1, mar + 1):
        z, y, x = np.where(lav == i)
        curr_z = z.max()
        if curr_z > z_max:
            curr_z = z_max
            coords = (z, y, x)

        if (curr_z == z_max) and (volumes[i] > volumes[max_marker]):
            coords = (z, y, x)

        err_lung[coords] = 0
    return err_lung


def costal_surface(lung, z_coords, max_coor, combined):
    """
    The convexity is determined by comparing the costal lung surface
    in axial slices to the convex hull of this costal lung surface.

    Args:
        lung: Cumulative x-position in lung.
        z_coords: z-coordinates in lung.
        max_coor: Threshold for the сostal surface for the lung.
        combined: Segmented lung (left or right).

    Returns:
        lung: Cumulative x-position in lung.
        erroneus: Errors in lungs.
        erroneus_erosion: Errors in lungs after mathematical morphology.
    """
    erroneus = np.zeros(lung.shape)
    for coord in np.unique(z_coords):
        if max_coor == .8:
            roi = (lung[coord] < max_coor) * (lung[coord] != 0)
        else:
            roi = (lung[coord] > max_coor) * (lung[coord] != 0)

        erroneus[coord] = skimage.morphology.convex_hull_object(roi) - roi

    erroneus = erroneus * (1 - (combined != 0))
    skm_ball = skimage.morphology.ball(RADIUS_BALL)
    erroneus_erosion = scipy.ndimage.morphology.binary_erosion(erroneus, structure=skm_ball)
    erroneus_erosion = scipy.ndimage.morphology.binary_dilation(erroneus_erosion, structure=skm_ball)

    return lung, erroneus, erroneus_erosion


def detection_lung_error(left, right):
    """
    Automatic error detection.

    The function aggregates cumulation, costal_surface, ventricular_extraction.
    Args:
        left: A mask of the left segmented lung.
        right: A mask of the right segmented lung.

    Returns:
        lung_l: A mask of the left segmented lung.
        lung_r: A mask of the right segmented lung.
    """

    lung_right_c = right.astype(float)
    lung_left_c = left.astype(float)

    lung_right_comm, z_coords_r = cumulation(lung_right_c)
    lung_left_comm, z_coords_l = cumulation(lung_left_c)

    lung_left_1, er_l, erroneus_erosion_left = costal_surface(lung_left_comm, z_coords_l, .2, lung_left_c)
    lung_right_1, er_r, erroneus_erosion_right = costal_surface(lung_right_comm, z_coords_r, .8, lung_right_c)

    erroneus_erosion_left = ventricular_extraction(erroneus_erosion_left.copy())
    erroneus_erosion_right = ventricular_extraction(erroneus_erosion_right.copy())
    erroneus_erosion_left = ventricular_extraction(erroneus_erosion_left)
    erroneus_erosion_right = ventricular_extraction(erroneus_erosion_right)

    lung_l = left + erroneus_erosion_left
    lung_r = right + erroneus_erosion_right

    return lung_l, lung_r


def improved_lung_segmentation(patient):
    """
    Improved lung segmentation.

    Args:
        patient: A label of CT.

    Returns:
        lungs: A mask of the segmented lungs
        lung_left: A mask of the left segmented lung.
        lung_right: A mask of the right segmented lung.
        trachea: A mask of the trachea.
    """

    right, left, trachea = conventional_lung_segmentation(patient)
    lung_left, lung_right = detection_lung_error(left, right)
    lungs = lung_left + lung_right

    return lungs, lung_left, lung_right, trachea
