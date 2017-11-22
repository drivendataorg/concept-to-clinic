import numpy as np
from keras.callbacks import ModelCheckpoint
from keras.engine import Input, Model
from keras.layers import Conv3D, MaxPooling3D, UpSampling3D, Activation
from keras.optimizers import Adam
from scipy.ndimage import zoom

from .segmentation_model import SegmentationModel


class Simple3DModel(SegmentationModel):
    def __init__(self):
        def simple_model_3d(input_shape, downsize_filters_factor=32, pool_size=(2, 2, 2), n_labels=1,
                            initial_learning_rate=0.01):
            """
            Builds a simple 3D classification model.
            :param input_shape: Shape of the input data (x_size, y_size, z_size, n_channels).
            :param downsize_filters_factor: Factor to which to reduce the number of filters. Making this value larger
            will reduce the amount of memory the model will need during training.
            :param pool_size: Pool size for the max pooling operations.
            :param n_labels: Number of binary labels that the model is learning.
            :param initial_learning_rate: Initial learning rate for the model. This will be decayed during training.
            :return: Untrained simple 3D Model
            """
            inputs = Input(input_shape)
            conv1 = Conv3D(int(32 / downsize_filters_factor), (3, 3, 3), activation='relu', padding='same')(inputs)
            pool1 = MaxPooling3D(pool_size=pool_size)(conv1)
            conv2 = Conv3D(int(64 / downsize_filters_factor), (3, 3, 3), activation='relu', padding='same')(pool1)
            up1 = UpSampling3D(size=pool_size)(conv2)
            conv8 = Conv3D(n_labels, (1, 1, 1))(up1)
            act = Activation('sigmoid')(conv8)
            model = Model(inputs=inputs, outputs=act)

            model.compile(optimizer=Adam(lr=initial_learning_rate), loss='binary_crossentropy',
                          metrics=['binary_crossentropy'])

            return model

        self.input_shape = (128, 128, 256, 1)
        self.scale_factor = 1 / 4.0
        self.model = simple_model_3d(input_shape=self.input_shape)
        self.best_model_path = super(Simple3DModel, self).get_best_model_path()

    def _fit(self, X, y):
        # Scale the bigger 3D input images to the desired smaller shape
        X_rescaled = np.zeros((X.shape[0], *self.input_shape))
        y_rescaled = np.zeros((X.shape[0], *self.input_shape))
        for i in range(X.shape[0]):
            X_rescaled[i, :, :, :, 0] = zoom(X[i, :, :, :, 0], self.scale_factor)
            y_rescaled[i, :, :, :, 0] = zoom(y[i, :, :, :, 0], self.scale_factor)
        model_checkpoint = ModelCheckpoint(self.best_model_path, monitor='loss', verbose=1, save_best_only=True)
        self.model.fit(X_rescaled, y_rescaled, callbacks=[model_checkpoint], epochs=10)

    def _predict(self, X):
        y_predicted = np.zeros_like(X)

        # Scale the bigger 3D input images to the desired smaller shape
        X_rescaled = np.zeros((1, *self.input_shape))
        X_rescaled[0, :, :, :, 0] = zoom(X[0, :, :, :, 0], self.scale_factor)

        X_predicted = self.model.predict(X_rescaled)
        y_predicted[0, :, :, :, 0] = zoom(X_predicted[0, :, :, :, 0], 1 / self.scale_factor)
        return y_predicted
