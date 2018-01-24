import abc
import collections


class ClassificationModel(abc.ABC):
    """

    Args:
        init_model (bool | str): whether to initialise the model.
            If str, then the model will be loaded from the init_model
            path.
        pull_size (int): maximum amount of batches allowed to be stored in RAM.
    """

    @abc.abstractmethod
    def __init__(self, init_model=True, pull_size=10, batch_size=32, data_format=None):
        self.model = None
        if not isinstance(batch_size, int):
            raise ValueError('`batch_size` should be of type int')
        if batch_size < 1:
            raise ValueError('`batch_size` should be grater or equal to 1')
        self.batch_size = batch_size
        if not isinstance(pull_size, int):
            raise ValueError('`pull_size` should be of type int')
        if pull_size < 1:
            raise ValueError('`pull_size` should be grater or equal to 1')
        self.pull_ct = collections.deque(maxlen=pull_size)
        self.pull_patches = list()

        self.data_format = data_format
        self.set_params()

        if init_model:
            if isinstance(init_model, str):
                self.model = self.load_model(init_model)
            else:
                self.model = self.init_model()

    @abc.abstractmethod
    def init_model(self):
        pass

    @abc.abstractmethod
    def load_model(self, model_path):
        """Load model method.

        Args:
            model_path (str): A path to the model.

        Returns:
            Model
        """
        pass

    @abc.abstractmethod
    def _ct_preprocess(self, ct_path):
        pass

    @abc.abstractmethod
    def _batch_process(self, batch, labels):
        pass

    @abc.abstractmethod
    def feed(self, annotations, sampling_pure, sampling_cancerous):
        """Train the model through the annotated CT scans

                Args:
                    annotations (list[dict]): A list of centroids of the form::
                         {'file_path': str,
                          'centroids': [{'x': int,
                                         'y': int,
                                         'z': int,
                                         'cancerous': bool}, ..]}.
                    sampling_pure (float): coefficient of .
                    sampling_cancerous (float): .

                Yields:
                    list[np.nd  array]: list of patches.
        """
        pass

    @abc.abstractmethod
    def train(self, annotations, train_val_split):
        """Train the model through the annotated CT scans

        Args:
            annotations (list[dict]): A list of centroids of the form::
                 {'file_path': str,
                  'centroids': [{'x': int,
                                 'y': int,
                                 'z': int,
                                 'cancerous': bool}, ..]}.

        Returns:
            tf.model: a model trained over annotated data.
        """
        pass

    @abc.abstractmethod
    def predict(self, candidates, model_path=None):
        """ Predict cancerous of given candidates.

        Args:
            candidates (list[dict]): A list of centroids of the form::
                {'file_path': str,
                 'centroids': {'x': int,
                               'y': int,
                               'z': int}}
            model_path (str): A path to the serialized model


        Returns:
            (list[dict]): A list of centroids of the form::
                {'file_path': str,
                 'centroids': {'x': int,
                               'y': int,
                               'z': int,
                               'p_concerning': float}}
        """
        pass
