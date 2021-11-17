from pymongo import MongoClient
import json
import requests
from time import sleep


class MongoConnection:
    def __init__(self, mongo_uri="localhost", port="27017"):
        self.client = MongoClient(f'mongodb://{mongo_uri}:{port}/')
        self.db = self.client.dltn
        self.collection = self.db.provider

    def find_manifest(self, id):
        r = self.collection.find_one({"manifest_id": id})
        return r

    def get_all_items_with_contents(self):
        r = self.collection.find({"contents": { "$exists": True} })
        return r


class MongoWriter(MongoConnection):
    def __init__(self, provider, data, mongo_uri="localhost", port="27017"):
        super().__init__(mongo_uri, port)
        self.provider = provider
        self.data = data

    def update_initial_manifest_record(self, activity):
        """@todo Need to Modify for Endtime.

        Currently looks to see if manfiest exists first. If not, adds.
        """
        exists = self.find_manifest(activity['manifest_url'])
        if exists is None:
            r = self.collection.update(
                {
                    "manifest_id": activity["manifest_url"]
                },
                {
                    "provider": self.provider,
                    "manifest_id": activity["manifest_url"],
                    "endtime": activity["endtime"],
                    "most_recent_activity": activity["type"]
                },
                upsert = True,
            )
            return r
        else:
            return {"message": "Already exists."}

    def __update_contents(self, manifest, data):
        r = self.collection.update_one(
            {
                "manifest_id": manifest
            },
            {
                "$set": {
                    "contents": data
                }
            },
            upsert=True
        )
        return r

    def __get_important_details(self, details):
        """Details we want:
                    @context
                    label
                    metadata
                    within

        """
        value = {
            "@context": details["@context"],
            "label": details['label'],
            'metadata': details['metadata']
        }
        if 'within' in details.keys():
            value['within'] = details['within']
        return value

    def add_contents_to_manifest_record_if_not_exists(self):
        missing_contents = self.collection.find_one({"contents": { "$exists": False} })
        r = requests.get(missing_contents['manifest_id'])
        if r.status_code == 200:
            details = self.__get_important_details(r.json())
            return self.__update_contents(missing_contents['manifest_id'], details)
        if r.status_code == 404:
            details = {"empty": True}
            return self.__update_contents(missing_contents['manifest_id'], details)
        else:
            print(f"{r.status_code} on {missing_contents['manifest_id']}")
            sleep(6)
            return "Sleeping"


class DLTNQuery(MongoConnection):
    """Class specific for broad DLTN queries."""
    def __init__(self, mongo_uri="localhost", port="27017"):
        super().__init__(mongo_uri, port)

    def get_all_metadata_labels(self):
        r = self.collection.distinct("contents.metadata.label")
        return list(r)

    def get_total_records_from_a_provider(self, provider):
        r = self.collection.find({"provider": provider})
        return len(list(r))


if __name__ == "__main__":
    utc_data = 'knox.json'
    with open(utc_data, 'rb') as my_data:
        data = json.load(my_data)

    test = MongoWriter('knox', data)

    ### Initialize records
    # for item in data['data']:
    #     print(test.update_initial_manifest_record(item))

    ### Update Metadata and Sleep
    # while True:
    #     print(test.add_contents_to_manifest_record_if_not_exists())

    ### Get Everything with Contents
    # x = test.get_all_items_with_contents()
    # print(len(list(x)))

    ### Test DLTNQuery
    test = DLTNQuery()
    print(test.get_total_records_from_a_provider('utc'))

    #print(test.add_contents_to_manifest_record_if_not_exists())
    #print(test.update_initial_manifest_record(data['data'][1]))
    #print(test.find_manifest('https://cdm16877.contentdm.oclc.org/digital/iiif-info/p16877coll15/23574/manifest.jsonn'))
