import sys
import time

import requests

TIMEOUT = 180
LOCALHOST = "http://localhost:{}/"
SERVICE_PORTS = {"INTERFACE": {"PORT": 8000, "SITES": ["api"]},
                 "VUE": {"PORT": 8080, "SITES": []},
                 "PREDICTION": {"PORT": 8001, "SITES": ["classify/predict/",
                                                        "identify/predict/",
                                                        "segment/predict/"]},
                 "DOCUMENTATION": {"PORT": 8002, "SITES": []}}


def page_errors(url):
    print("Fetching {} ...".format(url))
    response = requests.get(url)
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as http_error:
        print(http_error)
        return True
    return False


if __name__ == '__main__':
    one_failed = False
    start_time = time.time()
    services_to_test = list(SERVICE_PORTS.keys())

    while time.time() - start_time < TIMEOUT:
        for service in services_to_test:
            try:
                base_url = LOCALHOST.format(SERVICE_PORTS[service]["PORT"])
                response = requests.get(base_url)
            except requests.exceptions.ConnectionError as e:
                print("{} - not up yet. Continuing with next service...".format(base_url))
                continue
            except Exception as e:
                print("{} - Unexpected exception occurred: {}".format(base_url, e))
                one_failed = True

            one_failed |= page_errors(base_url)
            for site in SERVICE_PORTS[service]["SITES"]:
                one_failed |= page_errors(base_url + site)
            services_to_test.remove(service)

        if not services_to_test:
            sys.exit(1 if one_failed else 0)
        time.sleep(1)

    closed_ports = [SERVICE_PORTS[service]["PORT"] for service in SERVICE_PORTS.keys()]
    print("Time limit of {} seconds exceeded. Following ports did not open in time: {}".format(TIMEOUT, closed_ports))
    sys.exit(1)
