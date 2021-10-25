import requests


class ChangeDiscoveryRequest:
    """A base class for doing various change discovery requests."""
    def __init__(self, url, type_value):
        self.endpoint = url
        self.type = type_value
        self.details = requests.get(url).json()

    def validate_type(self):
        if "type" in self.details:
            if self.details["type"] != self.type:
                raise ValueError(f"{self.endpoint} should be of type {self.type} but is {self.details['type']}.")
        else:
            raise KeyError(f"{self.type} is missing a type value.")
        return

    def validate_id(self):
        if "id" in self.details:
            if not self.details["id"].startswith("https"):
                raise ValueError(f"{self.type} id does not start with https.")
        else:
            raise KeyError(f"{self.type} missing id.")
        return


class OrderedCollection(ChangeDiscoveryRequest):
    """A class to represent an ActivityStreams Collection."""
    def __init__(self, url, last_crawl=""):
        super().__init__(url, "OrderedCollection")
        self.__validate()
        self.processed_items = []
        self.last_crawl = last_crawl
        self.only_delete = False

    def __validate(self):
        self.validate_id()
        self.validate_type()
        if "last" not in self.details:
            raise KeyError("OrderedCollection missing required last property.")
        return

    def get_all_pages_ever(self):
        """This gets everything regardless of type or timestamp"""
        x = self.__crawl(self.details['last']['id'])
        while x is not False:
            self.__crawl(x)
        return

    def __crawl(self, page):
        current = ActivitiesPage(page)
        for activity in current.parsed_activities:
            self.processed_items.append(activity)
        if current.is_last_page == False:
            return current.details['prev']['id']
        else:
            return False


class ActivitiesPage(ChangeDiscoveryRequest):
    """A Class to represent an ActivityStreams CollectionPage"""
    def __init__(self, url, last_crawl=""):
        super().__init__(url, "OrderedCollectionPage")
        self.__validate()
        self.is_last_page = self.__test_if_last_page()
        self.activities = [activity for activity in reversed(self.details['orderedItems'])]
        self.parsed_activities = self.__parse_activities()

    def __validate(self):
        self.validate_id()
        self.validate_type()
        self.__validate_ordered_items()
        return

    def __validate_ordered_items(self):
        if "orderedItems" in self.details:
            if type(self.details['orderedItems']) == list:
                if len(self.details['orderedItems']) < 1:
                    raise ValueError("ActivitiesPage must include at least 1 item.")
            else:
                raise ValueError("orderedItems property on ActivitiesPage must be an array.")
        else:
            raise KeyError("ActivitiesPage missing orderedItems list.")

    def __test_if_last_page(self):
        if 'prev' not in self.details:
            return True
        else:
            return False

    def __parse_activities(self):
        """This is a work in progress.  Currently, timestamp and activity type not being actioned upon."""
        return [Activity(activity).parsed_activity for activity in self.activities]


class Activity:
    def __init__(self, activity_object):
        self.activity = activity_object
        self.parsed_activity = self.__parse_activity()

    def __validate(self):
        valid_types = ('Create', 'Update', 'Delete', 'Move', 'Add', 'Remove', 'Refresh')
        if self.activity['type'] not in valid_types:
            raise ValueError(f"Activity type is not valid. Got {self.activity['type']}.")

    def __get_endtime_if_exists(self):
        if 'endTime' in self.activity:
            return self.activity['endTime']
        else:
            return False

    def __parse_activity(self):
        """Looks at the object of an activity and returns appropriate data if a manifest is the subject."""
        if self.activity['object']['type'] == 'Manifest':
            return {
                'type': self.activity['type'],
                'manifest_url': self.activity['object']['id'],
                'endtime': self.__get_endtime_if_exists()
            }
        else:
            return {'type': 'Ignore'}


if __name__ == "__main__":
    x = OrderedCollection('https://iiif.bodleian.ox.ac.uk/iiif/activity/all-changes')
    x.get_all_pages_ever()
    print(x.processed_items)

