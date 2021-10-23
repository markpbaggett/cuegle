import requests


class ChangeDiscoveryRequest:
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


class OrderedCollection(ChangeDiscoveryRequest):
    def __init__(self, url):
        super().__init__(url, "OrderedCollection")
        self.__validate()

    def __validate(self):
        self.__validate_id()
        self.validate_type()
        if "last" not in self.details:
            raise KeyError("OrderedCollection missing required last property.")
        return

    def __validate_id(self):
        if "id" in self.details:
            if not self.details["id"].startswith("https"):
                raise ValueError("OrderedCollection id does not start with https.")
        else:
            raise KeyError("OrderedCollection missing id.")
        return


if __name__ == "__main__":
    OrderedCollection("https://iiif.bodleian.ox.ac.uk/iiif/activity/page-0")
