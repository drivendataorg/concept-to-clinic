import sys
import os
import pytest
import torch  # noqa # pylint: disable=unused-import

sys.path.append(os.path.join(os.path.dirname(__file__),
                             os.path.pardir,
                             os.path.pardir))


def skip_slow_test():
    """
    Skip the wrapped test function unless the environment variable RUN_SLOW_TESTS is set.
    """
    value = os.environ.get('RUN_SLOW_TESTS', '')
    return value.lower() not in {'1', 'true'}


skip_if_slow = pytest.mark.skipif(skip_slow_test(), reason='Takes very long')
