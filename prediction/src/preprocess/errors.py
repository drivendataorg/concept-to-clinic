
class EmptyDicomSeriesException(Exception):
    """Exception that is raised when the given folder does not contain dcm-files.
    """

    def __init__(self, *args):
        if not args:
            args = ('The specified path does not contain dcm-files. Please ensure that '
                    'the path points to a folder containing a DICOM-series.', )
        Exception.__init__(self, *args)
