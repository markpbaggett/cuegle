import requests


class ChangeDiscovery:
    def __init__(self, endpoint):
        self.endpoint = endpoint
        self.details = requests.get(endpoint).json()
        self.total = self.details['total']


if __name__ == "__main__":
    x = ChangeDiscovery('https://researchworks.oclc.org/digital/activity-stream/site/16311')
    print(x.total)