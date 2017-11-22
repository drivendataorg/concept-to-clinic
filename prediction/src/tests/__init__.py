import sys
import os
import torch  # noqa # pylint: disable=unused-import

sys.path.append(os.path.join(os.path.dirname(__file__),
                             os.path.pardir,
                             os.path.pardir))


def get_timeout():
    """
    If RUN_SLOW_TESTS is set to True, all tests should be run. Thus, no timeout is desired and this returns 0.
    Otherwise the content of TESTS_TIMEOUT is returned.
    :return: Time limit after which certain tests should be stopped
    """
    DEFAULT_TIMEOUT = 15
    run_slow_tests_variable = os.environ.get('RUN_SLOW_TESTS', '')
    run_slow_tests = (run_slow_tests_variable.lower() in {'1', 'true'})
    if run_slow_tests:
        return 0
    else:
        return int(os.environ.get('TESTS_TIMEOUT', DEFAULT_TIMEOUT))
