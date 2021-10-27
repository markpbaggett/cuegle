import requests


class ChangeDiscoveryRequest:
    """A base class for doing change discovery requests.

    All ChangeDiscovery types that are tied to an HTML request should inherit from this class.

    Attributes:
        endpoint (str): The url to the web resource you are processing.
        type (str): The corresponding ActivityStreams type class.  Used in validation.
        details (dict): The contents of the corresponding URL request.

    """
    def __init__(self, url, type_value):
        self.endpoint = url
        self.type = type_value
        self.details = requests.get(url).json()

    def validate_type(self):
        """Validates that contents of the request matches its intended type or raises an error."""
        if "type" in self.details:
            if self.details["type"] != self.type:
                raise ValueError(f"{self.endpoint} should be of type {self.type} but is {self.details['type']}.")
        else:
            raise KeyError(f"{self.type} is missing a type value.")
        return

    def validate_id(self):
        """Validates that the contents of the request has an id and starts with HTTPS or raises an error."""
        if "id" in self.details:
            if not self.details["id"].startswith("https"):
                raise ValueError(f"{self.type} id does not start with https.")
        else:
            raise KeyError(f"{self.type} missing id.")
        return


class OrderedCollection(ChangeDiscoveryRequest):
    """Represents an Ordered Collection request according to IIIF Change Discovery 1.0.

    Attributes:
        processed_items (list): A list of IIIF objects processed during this aggregation.
        last_crawl (str): The timestamp of the last time the collection was aggregated.
        only_delete (bool): State to help with refresh, remove, and delete instructions.

    """
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
        """Temporary method.  Used to process all pages ever regardless of Activity status."""
        x = self.__crawl(self.details['last']['id'])
        while x is not False:
            x = self.__crawl(x)
            print(x)
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
    """Represents an Ordered Collection Page according to IIIF Change Discovery 1.0.

    Attributes:
        is_last_page (bool): States whether this page is the last page in the collection.
        activities (list): A list of Activities in reverse order.
        parsed_activities (list): @todo what is this again?
    """
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
    """Represents an Activity for IIIF Change Discovery 1.0.

    Attributes:
        activity (dict): The corresponding activity with all metadata.
        parsed_activity (dict): An activity with only the metadata we need for the aggregator.

    """
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
    x = OrderedCollection('https://researchworks.oclc.org/digital/activity-stream/site/16877')
    activities = x.get_all_pages_ever()
    with open("utc_activities.py", 'w') as sample:
        sample.write(activities)

