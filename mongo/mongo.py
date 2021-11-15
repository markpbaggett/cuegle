from pymongo import MongoClient
import json
import requests


class MongoWriter:
    def __init__(self, provider, data, mongo_uri="localhost", port="27017"):
        self.client = MongoClient(f'mongodb://{mongo_uri}:{port}/')
        self.db = self.client.dltn
        self.collection = self.db.provider
        self.provider = provider
        self.data = data

    def update_initial_manifest_record(self, activity):
        """Need to Modify for Endtime"""
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

    def __update_contents(self, manifest, data):
        r = self.collection.update(
            {
                "manifest_id": manifest
            },
            {
                "contents": data
            },
            upsert = True
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
        if 'within' in details.items():
            value['within'] = details['within']
        return value

    def add_contents_to_manifest_record_if_not_exists(self):
        missing_contents = self.collection.find_one({"contents": { "$exists": False} })
        r = requests.get(missing_contents['manifest_id'])
        return self.__update_contents(missing_contents['manifest_id'], self.__get_important_details(r.json()))


if __name__ == "__main__":
    utc_data = 'utk_activities.json'
    with open(utc_data, 'rb') as my_data:
        data = json.load(my_data)

    test = MongoWriter('utk', data)
    #print(test.update_initial_manifest_record(data['data'][0]))
    print(test.add_contents_to_manifest_record_if_not_exists())
