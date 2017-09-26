# limit memory usage..
import glob
import logging
import os

import cv2
import numpy
import pandas
# limit memory usage..
from keras import backend as K
from keras.layers import Input, Convolution3D, MaxPooling3D, Flatten, AveragePooling3D
from keras.metrics import binary_accuracy, binary_crossentropy, mean_absolute_error
from keras.models import Model
from keras.optimizers import SGD

from . import helpers

CUBE_SIZE = 32
MEAN_PIXEL_VALUE = 41
EXTRACTED_IMAGE_DIR = "data/extracted/"
NODULE_DETECTION_DIR = "data/detections/"
K.set_image_dim_ordering("tf")
POS_WEIGHT = 2
NEGS_PER_POS = 20
P_TH = 0.6
LEARN_RATE = 0.001
PREDICT_STEP = 12


def load_patient_images(patient_id, base_dir=EXTRACTED_IMAGE_DIR, wildcard="*.*", exclude_wildcards=None):
    exclude_wildcards = exclude_wildcards or []
    src_dir = os.path.join(os.getcwd(), base_dir, patient_id)
    src_img_paths = glob.glob(src_dir + wildcard)
    for exclude_wildcard in exclude_wildcards:
        exclude_img_paths = glob.glob(src_dir + exclude_wildcard)
        src_img_paths = [im for im in src_img_paths if im not in exclude_img_paths]
    src_img_paths.sort()
    images = [cv2.imread(img_path, cv2.IMREAD_GRAYSCALE) for img_path in src_img_paths]
    images = [im.reshape((1,) + im.shape) for im in images]
    res = numpy.vstack(images)
    return res


def prepare_image_for_net3D(img):
    img = img.astype(numpy.float32)
    img -= MEAN_PIXEL_VALUE
    img /= 255.
    img = img.reshape(1, img.shape[0], img.shape[1], img.shape[2], 1)
    return img


def filter_patient_nodules_predictions(df_nodule_predictions: pandas.DataFrame, patient_id, view_size):
    patient_mask = load_patient_images(patient_id, wildcard="*_m.png")
    delete_indices = []
    for index, row in df_nodule_predictions.iterrows():
        z_perc = row["coord_z"]
        y_perc = row["coord_y"]
        center_x = int(round(row["coord_x"] * patient_mask.shape[2]))
        center_y = int(round(y_perc * patient_mask.shape[1]))
        center_z = int(round(z_perc * patient_mask.shape[0]))

        mal_score = row["diameter_mm"]
        start_y = center_y - view_size / 2
        start_x = center_x - view_size / 2
        nodule_in_mask = False
        for z_index in [-1, 0, 1]:
            img = patient_mask[z_index + center_z]
            start_x = int(start_x)
            start_y = int(start_y)
            view_size = int(view_size)
            img_roi = img[start_y:start_y + view_size, start_x:start_x + view_size]
            if img_roi.sum() > 255:  # more than 1 pixel of mask.
                nodule_in_mask = True

        if not nodule_in_mask:
            logging.info("Nodule not in mask: ", (center_x, center_y, center_z))
            if mal_score > 0:
                mal_score *= -1
            df_nodule_predictions.loc[index, "diameter_mm"] = mal_score
        else:
            if center_z < 30:
                logging.info("Z < 30: ", patient_id, " center z:", center_z, " y_perc: ", y_perc)
                if mal_score > 0:
                    mal_score *= -1
                df_nodule_predictions.loc[index, "diameter_mm"] = mal_score

            if (z_perc > 0.75 or z_perc < 0.25) and y_perc > 0.85:
                logging.info("SUSPICIOUS FALSEPOSITIVE: ", patient_id, " center z:", center_z, " y_perc: ", y_perc)

            if center_z < 50 and y_perc < 0.30:
                logging.info("SUSPICIOUS FALSEPOSITIVE OUT OF RANGE: ", patient_id, " center z:", center_z, " y_perc: ",
                             y_perc)

    df_nodule_predictions.drop(df_nodule_predictions.index[delete_indices], inplace=True)
    return df_nodule_predictions


def get_net(input_shape=(CUBE_SIZE, CUBE_SIZE, CUBE_SIZE, 1), load_weight_path=None) -> Model:
    """Load the pre-trained 3D ConvNet that should be used to predict a nodule and its malignancy.

    Args:
        input_shape: shape of the input layer. Defaults to (CUBE_SIZE, CUBE_SIZE, CUBE_SIZE, 1).
        load_weight_path: path of the trained model weights.

    Returns:
        keras.models.Model
    """
    inputs = Input(shape=input_shape, name="input_1")
    x = inputs
    x = AveragePooling3D(pool_size=(2, 1, 1), strides=(2, 1, 1), padding="same")(x)
    x = Convolution3D(64, (3, 3, 3), activation='relu', padding='same', name='conv1', strides=(1, 1, 1))(x)
    x = MaxPooling3D(pool_size=(1, 2, 2), strides=(1, 2, 2), padding='valid', name='pool1')(x)

    # 2nd layer group
    x = Convolution3D(128, (3, 3, 3), activation='relu', padding='same', name='conv2', strides=(1, 1, 1))(x)
    x = MaxPooling3D(pool_size=(2, 2, 2), strides=(2, 2, 2), padding='valid', name='pool2')(x)

    # 3rd layer group
    x = Convolution3D(256, (3, 3, 3), activation='relu', padding='same', name='conv3a', strides=(1, 1, 1))(x)
    x = Convolution3D(256, (3, 3, 3), activation='relu', padding='same', name='conv3b', strides=(1, 1, 1))(x)
    x = MaxPooling3D(pool_size=(2, 2, 2), strides=(2, 2, 2), padding='valid', name='pool3')(x)

    # 4th layer group
    x = Convolution3D(512, (3, 3, 3), activation='relu', padding='same', name='conv4a', strides=(1, 1, 1))(x)
    x = Convolution3D(512, (3, 3, 3), activation='relu', padding='same', name='conv4b', strides=(1, 1, 1), )(x)
    x = MaxPooling3D(pool_size=(2, 2, 2), strides=(2, 2, 2), padding='valid', name='pool4')(x)

    last64 = Convolution3D(64, (2, 2, 2), activation="relu", name="last_64")(x)
    out_class = Convolution3D(1, (1, 1, 1), activation="sigmoid", name="out_class_last")(last64)
    out_class = Flatten(name="out_class")(out_class)

    out_malignancy = Convolution3D(1, (1, 1, 1), activation=None, name="out_malignancy_last")(last64)
    out_malignancy = Flatten(name="out_malignancy")(out_malignancy)

    model = Model(input=inputs, output=[out_class, out_malignancy])
    model.load_weights(load_weight_path)

    model.compile(optimizer=SGD(lr=LEARN_RATE, momentum=0.9, nesterov=True),
                  loss={"out_class": "binary_crossentropy", "out_malignancy": mean_absolute_error},
                  metrics={"out_class": [binary_accuracy, binary_crossentropy], "out_malignancy": mean_absolute_error})

    return model


def predict_cubes(model_path, patient_id, magnification=1, ext_name=""):  # noqa: C901 TODO: reduce complexity
    """Return a DataFrame including position, diameter and chance of abnormal tissue to be a nodule.

    Args:
        model_path: path to the pre-trained model that should be used for the prediction
        patient_id: SeriesInstanceUID of the patient
        magnification: what magnification for the model to use, one of (1, 1.5, 2)
        ext_name: external name of the model, one of ("luna16_fs", "luna_posnegndsb_v")

    Returns:
        pandas.DataFrame containing anno_index, coord_x, coord_y, coord_z, diameter, nodule_chance, diameter_mm
        of each found nodule.
    """

    dst_dir = NODULE_DETECTION_DIR
    if not os.path.exists(dst_dir):
        os.makedirs(dst_dir)

    holdout_ext = ""
    flip_ext = ""

    dst_dir += "predictions" + str(int(magnification * 10)) + holdout_ext + flip_ext + "_" + ext_name + "/"
    if not os.path.exists(dst_dir):
        os.makedirs(dst_dir)

    model = get_net(input_shape=(CUBE_SIZE, CUBE_SIZE, CUBE_SIZE, 1),
                    load_weight_path=model_path)
    patient_ids = [patient_id]
    for file_name in os.listdir(EXTRACTED_IMAGE_DIR):
        if not os.path.isdir(EXTRACTED_IMAGE_DIR + file_name):
            continue
        patient_ids.append(file_name)

    for patient_index, patient_id in enumerate(reversed(patient_ids)):
        logging.info(patient_index, ": ", patient_id)

        patient_img = load_patient_images(patient_id, wildcard="*_i.png", exclude_wildcards=[])
        if magnification != 1:
            patient_img = helpers.rescale_patient_images(patient_img, (1, 1, 1), magnification)

        patient_mask = load_patient_images(patient_id, wildcard="*_m.png", exclude_wildcards=[])
        if magnification != 1:
            patient_mask = helpers.rescale_patient_images(patient_mask, (1, 1, 1), magnification, is_mask_image=True)

        step = PREDICT_STEP
        CROP_SIZE = CUBE_SIZE

        predict_volume_shape_list = [0, 0, 0]
        for dim in range(3):
            dim_indent = 0
            while dim_indent + CROP_SIZE < patient_img.shape[dim]:
                predict_volume_shape_list[dim] += 1
                dim_indent += step

        predict_volume_shape = (
            predict_volume_shape_list[0], predict_volume_shape_list[1], predict_volume_shape_list[2])

        predict_volume = numpy.zeros(shape=predict_volume_shape, dtype=float)
        done_count = 0
        skipped_count = 0
        batch_size = 128
        batch_list = []
        batch_list_coords = []
        patient_predictions_csv = []
        annotation_index = 0
        logging.info("Predicted Volume Shape:" + str(predict_volume_shape))

        for z in range(0, predict_volume_shape[0]):
            for y in range(0, predict_volume_shape[1]):
                for x in range(0, predict_volume_shape[2]):
                    # if cube_img is None:
                    cube_img = patient_img[z * step:z * step + CROP_SIZE, y * step:y * step + CROP_SIZE,
                                           x * step:x * step + CROP_SIZE]
                    cube_mask = patient_mask[z * step:z * step + CROP_SIZE, y * step:y * step + CROP_SIZE,
                                             x * step:x * step + CROP_SIZE]

                    if cube_mask.sum() < 2000:
                        skipped_count += 1
                    else:
                        if CROP_SIZE != CUBE_SIZE:
                            cube_img = helpers.rescale_patient_images2(cube_img, (CUBE_SIZE, CUBE_SIZE, CUBE_SIZE))

                        img_prep = prepare_image_for_net3D(cube_img)
                        batch_list.append(img_prep)
                        batch_list_coords.append((z, y, x))
                        if len(batch_list) % batch_size == 0:
                            batch_data = numpy.vstack(batch_list)
                            p = model.predict(batch_data, batch_size=batch_size)
                            for i in range(len(p[0])):
                                p_z = batch_list_coords[i][0]
                                p_y = batch_list_coords[i][1]
                                p_x = batch_list_coords[i][2]
                                nodule_chance = p[0][i][0]
                                predict_volume[p_z, p_y, p_x] = nodule_chance
                                if nodule_chance > P_TH:
                                    p_z = p_z * step + CROP_SIZE / 2
                                    p_y = p_y * step + CROP_SIZE / 2
                                    p_x = p_x * step + CROP_SIZE / 2

                                    p_z_perc = round(p_z / patient_img.shape[0], 4)
                                    p_y_perc = round(p_y / patient_img.shape[1], 4)
                                    p_x_perc = round(p_x / patient_img.shape[2], 4)
                                    diameter_mm = round(p[1][i][0], 4)
                                    diameter_perc = round(diameter_mm / patient_img.shape[2], 4)
                                    nodule_chance = round(nodule_chance, 4)
                                    patient_predictions_csv_line = [annotation_index, p_x_perc, p_y_perc, p_z_perc,
                                                                    diameter_perc, nodule_chance, diameter_mm]
                                    patient_predictions_csv.append(patient_predictions_csv_line)
                                    annotation_index += 1

                            batch_list = []
                            batch_list_coords = []
                    done_count += 1
                    if done_count % 10000 == 0:
                        logging.info("Done: ", done_count, " skipped:", skipped_count)

        df = pandas.DataFrame(patient_predictions_csv,
                              columns=["anno_index", "coord_x", "coord_y", "coord_z", "diameter", "nodule_chance",
                                       "diameter_mm"])
        filter_patient_nodules_predictions(df, patient_id, CROP_SIZE * magnification)

        return df
