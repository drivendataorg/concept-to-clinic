import keras
from keras.layers.merge import add, average


def _identity_block(input_tensor, kernel, filters, bn_axis, dropout=None):
    x = keras.layers.BatchNormalization(axis=bn_axis)(input_tensor)
    x = keras.layers.Activation('relu')(x)
    if dropout is not None:
        x = keras.layers.Dropout(dropout)(x)
    x = keras.layers.Conv3D(filters[0], (kernel, kernel, kernel), padding='same')(x)
    x = keras.layers.BatchNormalization(axis=bn_axis)(x)
    x = keras.layers.Activation('relu')(x)
    if dropout is not None:
        x = keras.layers.Dropout(dropout)(x)
    x = keras.layers.Conv3D(filters[1], (kernel, kernel, kernel), padding='same')(x)
    x = add([x, input_tensor])
    return x


def _conv_block(input_tensor, kernel, filters, bn_axis, dropout=None,
                stride=(1, 1, 1), mode='same'):
    x = keras.layers.BatchNormalization(axis=bn_axis)(input_tensor)
    x = keras.layers.Activation('relu')(x)
    if dropout is not None:
        x = keras.layers.Dropout(dropout)(x)
    if stride != (1, 1, 1):
        mode = 'valid'
    x = keras.layers.Conv3D(filters[0], (kernel, kernel, kernel), strides=stride, padding=mode)(x)
    x = keras.layers.BatchNormalization(axis=bn_axis)(x)
    x = keras.layers.Activation('relu')(x)
    if dropout is not None:
        x = keras.layers.Dropout(dropout)(x)
    x = keras.layers.Conv3D(filters[1], (kernel, kernel, kernel), padding='same')(x)
    shortcut = keras.layers.Conv3D(filters[1], (kernel, kernel, kernel),
                                   strides=stride, padding=mode)(input_tensor)
    x = add([x, shortcut])
    return x


def _encoder(in_tensor, stride, kernel, bn_axis, dropout=.2):
    x = keras.layers.Dropout(dropout)(in_tensor)
    x = keras.layers.Conv3D(32, (kernel[0], kernel[1], kernel[2]), padding='same')(x)
    x = keras.layers.BatchNormalization(axis=bn_axis)(x)
    x = keras.layers.Activation('relu')(x)
    x = keras.layers.Dropout(dropout)(x)
    x = keras.layers.MaxPooling3D((2, 2, 2))(x)

    x = _identity_block(x, 3, [32, 32], dropout=dropout, bn_axis=bn_axis)
    x = _conv_block(x, 3, [64, 64], stride=stride, dropout=dropout, bn_axis=bn_axis)
    x = _identity_block(x, 3, [64, 64], dropout=dropout, bn_axis=bn_axis)
    x = _conv_block(x, 3, [128, 128], dropout=dropout, bn_axis=bn_axis)
    x = _identity_block(x, 3, [128, 128], dropout=dropout, bn_axis=bn_axis)
    return x


def net(channel_axis):
    # Determine proper input shape
    in_shape = [(24, 42, 42, 1),
                (42, 24, 42, 1),
                (42, 42, 24, 1)]
    strides = [(1, 2, 2),
               (2, 1, 2),
               (2, 2, 1)]
    kernels = [(5, 5, 5),
               (5, 5, 5),
               (5, 5, 5)]
    dropout_conv = .2
    dropout_dence = .2

    inputs = [keras.layers.Input(shape=inx) for inx in in_shape]
    coders = [_encoder(in_tensor=tnsr, stride=stride, bn_axis=channel_axis,
                       kernel=kernel, dropout=dropout_conv)
              for tnsr, stride, kernel in zip(inputs, strides, kernels)]
    x = average(coders)

    #   shape:  128, 9, 10, 10
    x = _conv_block(x, 3, [128, 128], dropout=dropout_conv, bn_axis=channel_axis)
    x = _identity_block(x, 3, [128, 128], dropout=dropout_conv, bn_axis=channel_axis)
    x = _conv_block(x, 3, [256, 256], stride=(2, 2, 2), dropout=dropout_conv, bn_axis=channel_axis)
    x = _identity_block(x, 3, [256, 256], dropout=dropout_conv, bn_axis=channel_axis)
    x = keras.layers.BatchNormalization(axis=channel_axis)(x)
    x = keras.layers.Activation('relu')(x)
    x = keras.layers.AveragePooling3D((2, 2, 2))(x)

    x = keras.layers.Flatten()(x)
    x = keras.layers.Dropout(dropout_dence)(x)
    x = keras.layers.Dense(256)(x)
    x = keras.layers.LeakyReLU(.3)(x)
    x = keras.layers.Dropout(dropout_dence)(x)
    x = keras.layers.Dense(2, activation='softmax', name='is_nodule')(x)
    model = keras.models.Model(inputs, x)
    model.compile('adam', 'categorical_crossentropy')
    return model
