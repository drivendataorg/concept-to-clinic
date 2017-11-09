import sys
import requests

LOCALHOST = "http://localhost:{}/"
SERVICE_PORTS = {"INTERFACE":     {"PORT": 8000, "SITES": ["api"]},
                 "VUE":           {"PORT": 8080, "SITES": []},
                 "PREDICTION":    {"PORT": 8001, "SITES": ["classify/predict/",
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

    for service in SERVICE_PORTS.keys():
        base_url = LOCALHOST.format(SERVICE_PORTS[service]["PORT"])
        one_failed |= page_errors(base_url)
        for site in SERVICE_PORTS[service]["SITES"]:
            page_errors(base_url + site)

    if one_failed:
        sys.exit(1)
    sys.exit(0)
