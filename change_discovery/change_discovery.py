import requests


class ChangeDiscovery:
    def __init__(self, endpoint):
        self.endpoint = endpoint
        self.details = requests.get(endpoint).json()
        self.__confirm_collection()
        self.total = self.details['total']

    def __confirm_collection(self):
        try:
            if self.details['type'] != "OrderedCollection":
                raise ValueError('Type is not OrderedCollection')
        except KeyError:
            print("Type not defined.")

    def crawl_pages(self):
        initial = self.details['first']['id']
        self.__crawl_page(initial)

    def __crawl_page(self, page):
        x = Page(page)
        activities = []
        if x.is_last_page is False:
            try:
                for activitiy in x.activity_types:
                    print(activitiy)
                    if activitiy not in activities:
                        activities.append(activitiy)
                self.__crawl_page(x.next)
            except:
                pass
        return activities


class Page:
    def __init__(self, url):
        self.url = url
        self.details = requests.get(url).json()
        self.activities = self.__get_activities()
        self.activity_types = self.get_all_activity_types()
        self.is_last_page = self.__test_if_last()
        self.next = self.__get_next()

    def __get_activities(self):
        return [item for item in self.details['orderedItems']]

    def __test_if_last(self):
        if 'next' in self.details:
            return False
        else:
            return True

    def get_all_activity_types(self):
        return set([activity['type'] for activity in self.activities])

    def __get_next(self):
        if self.is_last_page is False:
            return self.details['next']['id']


if __name__ == "__main__":
    # x = ChangeDiscovery('https://researchworks.oclc.org/digital/activity-stream/site/16311')
    # x = Page('https://researchworks.oclc.org/digital/activity-stream/site/16311/1')
    # print(x.get_all_activity_types())
    x = ChangeDiscovery('https://researchworks.oclc.org/digital/activity-stream/site/16877').crawl_pages()
    print(x)