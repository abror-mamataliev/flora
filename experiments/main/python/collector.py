""" a thin client to talk to a flora server. """
import json

from google.protobuf.json_format import MessageToDict


class DataCollector:
    def __init__(self):
        self.data = []

    def add_record(self, i, config, scores):
        self.data.append({
            'iteration': i,
            'configuration': MessageToDict(config),
            'results': scores
        })

    def write_data(self, path):
        json.dump(self.data, open(path, 'w'))
