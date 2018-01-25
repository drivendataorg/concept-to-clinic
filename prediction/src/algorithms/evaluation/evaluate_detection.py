from config_submit import config as config_submit

import os
import numpy as np
import pandas
import csv

# IoverU threshold to decide if two rectangles from adjacent slices can be merged into a box
merge_rectangles_threshold = 0.4
# confidence score threshold used to filter out false positives
confidence_score_threshold = 4.0
# IoverU threshold to determine if a detection is correct
correct_detection_threshold = 0.4
# whether to use the prediction results when we try to filter out false positives
use_prediction_results = False

def intersection_over_union(boxA, boxB):
    # boxes should be strored as [x, y, width, height]
    startA = np.array(boxA[0:2])
    endA = startA + np.array(boxA[2:4])
    startB = np.array(boxB[0:2])
    endB = startB + np.array(boxB[2:4])

    overlap = []
    for i in range(len(startA)):
        overlap.append(max(0, min(endA[i], endB[i]) - max(startA[i], startB[i]) + 1))

    areaA = boxA[2] * boxA[3]
    areaB = boxB[2] * boxB[3]
    intersection = overlap[0] * overlap[1]
    union = areaA + areaB - intersection
    return areaA, areaB, intersection, intersection / union

def is_overlap(boxA, boxB):
    areaA, areaB, intersection, IoverU = intersection_over_union(boxA, boxB)
    if (intersection / areaA) > merge_rectangles_threshold or (intersection / areaB) > merge_rectangles_threshold:
        return True
    return False

def intersection_over_union_3D(boxA, boxB):
    # boxes should be strored as [x, y, z, width, height, depth]
    startA = np.array(boxA[0:3])
    endA = startA + np.array(boxA[3:6])
    startB = np.array(boxB[0:3])
    endB = startB + np.array(boxB[3:6])

    overlap = []
    for i in range(len(startA)):
        overlap.append(max(0, min(endA[i], endB[i]) - max(startA[i], startB[i]) + 1))

    intersection = overlap[0] * overlap[1] * overlap[2]
    union = boxA[3] * boxA[4] * boxA[5] + boxB[3] * boxB[4] * boxB[5] - intersection
    return intersection / union

def add_to_group(groups, boxA, boxB):
    pair_not_exist = True
    for group in groups:
        if boxA in group and boxB in group:
            # both boxA and boxB exist in the same group, do nothing
            pair_not_exist = False
        elif boxA in group:
            # boxA is in a group, check if boxB can be merged into the group
#            if intersection_over_union(group[-1], boxB) > merge_rectangles_threshold:
            if is_overlap(group[-1], boxB):
                group.append(boxB)
            pair_not_exist = False
    
    # both boxA and boxB do not exist in any group, create new group
    if pair_not_exist:
        group = []
        group.append(boxA)
        group.append(boxB)
        groups.append(group)

def groups_to_boxes(rectangles, groups):
    # merge rectangles in the same group into a 3D box
    boxes = []
    for group in groups:
        points = []
        for rect in group:
            points.append(rect[0:3])
            points.append([rect[0], rect[1] + rect[3] - 1, rect[2] + rect[4] - 1])
        min = np.min(points, axis=0)
        max = np.max(points, axis=0)
        # save the box as [x, y, z, width, height, depth]
        box = [min[1], min[2], min[0], max[1] - min[1] + 1, max[2] - min[2] + 1, max[0] - min[0] + 1]
        boxes.append(box)
    
    # deal with rectangles that haven't been added into any group
    for rect in rectangles:
        added_to_group = False
        for group in groups:
            if rect in group:
                added_to_group = True
        
        if not added_to_group:
            # create a box with single rectangle
            box = [rect[1], rect[2], rect[0], rect[3], rect[4], 1.0]
            boxes.append(box)
    
    return boxes

def group_rectangles(rectangles):
    num_rectangles = len(rectangles)
    groups = []
    for i in range(num_rectangles - 1):
        for j in range(i + 1, num_rectangles):
            # for each pair of rectangles
            boxA = rectangles[i]
            boxB = rectangles[j]
            
            # check if they are overlapped enough and close enough on z-axis
#            IoverU = intersection_over_union(boxA[1:], boxB[1:])
            if is_overlap(boxA[1:], boxB[1:]) and (boxB[0] - boxA[0]) < 3:
                # add these two rectangles into the same group
                add_to_group(groups, boxA, boxB)
    
    # convert groups into bounding boxes
    boxes = groups_to_boxes(rectangles, groups)
    return boxes;

def get_bounding_boxes(annotations):
    # for each annotation/ROI, find its bounding rectangle
    rectangles = []
    for annotation in annotations:
        num_of_points = int(annotation[19])
        image_no = int(annotation[0])
        points = []
        for i in range(num_of_points):
            # get pxX and pxY
            points.append([float(annotation[23+i*5]), float(annotation[24+i*5])])
        
        # find minimum and maximum of on both x and y axes
        min = np.min(points, axis=0)
        max = np.max(points, axis=0)
        
        # save the rectangle as [z-index, x, y, width, height]
        rectangle = [image_no, min[0], min[1], max[0] - min[0] + 1, max[1] - min[1] + 1]
        rectangles.append(rectangle)
    
    # group bounding rectangles into 3D bounding boxes
    bounding_boxes = group_rectangles(rectangles)
    return bounding_boxes

def gen_rows(stream, max_length=None):
      rows = csv.reader(stream)
      if max_length is None:
          rows = list(rows)
          max_length = max(len(row) for row in rows)
      for row in rows:
          yield row + [None] * (max_length - len(row))

# header of annotation files exported from OsiriX:
# ImageNo,RoiNo,RoiMean,RoiMin,RoiMax,RoiTotal,RoiDev,RoiName,RoiCenterX,RoiCenterY,RoiCenterZ,
# LengthCm,LengthPix,AreaPix2, AreaCm2,RoiType,SOPInstanceUID,SeriesInstanceUID,StudyInstanceUID,
# NumOfPoints,mmX,mmY,mmZ,pxX,pxY,...
# --> number of columns: 20 + NumOfPoints * 5
# note: z index (ImageNo) starts from 0
def load_annotations_OsiriX(path):
    bounding_boxes = []
    for file in os.listdir(path):
        filepath = os.path.join(path, file)
        with open(filepath) as f:
            df = pandas.DataFrame.from_records(list(gen_rows(f)))
        df.drop(0, inplace=True)    # drop the first row
        annotations = df.as_matrix()
        boxes = np.array(get_bounding_boxes(annotations))
        
        # concatenate with SeriesInstanceUID
        id = np.full((1, boxes.shape[0]), annotations[0][17], dtype=object)
        boxes = np.concatenate((id.T, boxes), axis=1)
        bounding_boxes.append(boxes)
    
    # concatenate into a single 2D array
    return np.concatenate(bounding_boxes)

# header of prediction file generated by grt123 testing script
# id,cancer
def get_prediction_probability(prediction, id):
    for predict in prediction:
        if predict[0] == id:
            return predict[1]
    return 0.0

# header of detection file generated by grt123 testing script
# id,confidence,z,y,x,size
# note: z index starts from 1 and unit of y, x, and size is px
# (don't need to convert to mm because the annotation files don't contain slice thickness information)
def filter_detections(prediction, detection):
    prep_result_path = config_submit['preprocess_result_path']
    detections = []
    for detect in detection:
        id = detect[0]
        # spacing: [slice_thickness, pixel_spacing_x, pixel_spacing_y]
        spacing = np.load(os.path.join(prep_result_path, id + '_info.npy'))[1]
        
        if use_prediction_results == True:
            confidence = detect[1] * get_prediction_probability(prediction, id)
        else:
            confidence = detect[1]
        
        if confidence > confidence_score_threshold:
            # each detection is a sphere
            diameter = detect[5]
            min = detect[3:5] - (diameter / 2)
            # handle z coordinate
            diameter_mm = detect[5] * spacing[1]
            diameter_slice = diameter_mm / spacing[0]
            minz = detect[2] - (diameter_slice / 2)
            # save the sphere as cube as [id, x, y, z, width, height, depth]
            cube = [id, min[1], min[0], minz - 1, diameter, diameter, diameter_slice]
            detections.append(cube)
    return detections

# header of detection file generated by grt123 testing script
# id,confidence,z,y,x,size
# note: z index starts from 1 and unit of y, x, and size is px
# output details in
# ['Dataset', 'Patient', 'StudyInstanceUID', 'SeriesInstanceUID', 'Cancer (%)', 'Confidence', 'ImageNo','CenterX (px)','CenterY (px)','Diameter (mm)']
def get_detection_detail(prediction, detection, filepaths):
    prep_result_path = config_submit['preprocess_result_path']
    details = []
    for detect in detection:
        id = detect[0]
        # spacing: [slice_thickness, pixel_spacing_x, pixel_spacing_y]
        spacing = np.load(os.path.join(prep_result_path, id + '_info.npy'))[1]
        rows, cols = np.where(filepaths == id)
        if rows.size == 0:
           print id, 'not found'
           continue
        probability = round(get_prediction_probability(prediction, id) * 100, 2)
        filepath = filepaths[rows][0]
        dataset = filepath[0]
        patient = filepath[1]
        studyInstanceUID = filepath[2]
        image_no = int(round(detect[2]))    # starts from 1 to sync with OsiriX
        diameter_mm = detect[5] * spacing[1]
        detail = [dataset, patient, studyInstanceUID, id, probability, detect[1], image_no, detect[4], detect[3], diameter_mm]
        details.append(detail)
    return np.array(details)

def compare_results(detections, annotations):
    correct_detection = 0
    for detect in detections:
        for annotate in annotations:
            if annotate[0] == detect[0]:
                IoverU = intersection_over_union_3D(detect[1:], annotate[1:])
                if IoverU > correct_detection_threshold:
                    correct_detection += 1
    return correct_detection

dataset = 'LUSC'
prediction_file = 'prediction_' + dataset + '.csv'
detection_file = 'detection_' + dataset + '.csv'
annotation_path = 'TCIA_annotation/TCGA-' + dataset
# for more details of detections
detection_detail_file = 'detection_detail_' + dataset + '.csv'
filepath = 'TCGA-' + dataset + '_filepath.npy'

df = pandas.read_csv(prediction_file)
prediction = df.as_matrix()

df = pandas.read_csv(detection_file)
detection = df.as_matrix()

if os.path.exists(filepath):
    filepaths = np.load(filepath)
    detection_detail = get_detection_detail(prediction, detection, filepaths)
    print detection_detail
    df = pandas.DataFrame(detection_detail)
    df.columns = ['Dataset', 'Patient', 'StudyInstanceUID', 'SeriesInstanceUID', 'Cancer (%)', 'Confidence', 'ImageNo','CenterX (px)','CenterY (px)','Diameter (mm)']
    df.to_csv(detection_detail_file, index=False)

detections = filter_detections(prediction, detection)
print 'number of detections:', len(detections)

annotations = load_annotations_OsiriX(annotation_path)
print 'number of annotations:', len(annotations)

correct_detection = compare_results(detections, annotations)
print 'number of correct_detection:', correct_detection

# calculate precision rate
if len(detections) == 0:
    precision = 0.0
else:
    precision = float(correct_detection) * 100 / len(detections)

# calculate recall rate
if len(annotations) == 0:
    recall = 0.0
else:
    recall = float(correct_detection) * 100 / len(annotations)

# calculate f-score
if precision == 0 and recall == 0:
    fscore = 0.0
else:
    fscore = 2 * precision * recall / (precision + recall)

print 'precision rate:',correct_detection,'/',len(detections),'(',round(precision, 2),'% )'
print 'recall rate:',correct_detection,'/',len(annotations),'(',round(recall, 2),'% )'
print 'f-score:',round(fscore, 2),'%'
