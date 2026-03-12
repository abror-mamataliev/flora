""" a thin client to talk to a flora server. """
import json

from math import sqrt

import grpc

from google.protobuf.json_format import MessageToDict

from flora_rendering_problem_service_pb2 import Empty, RenderingScore
from flora_rendering_problem_service_pb2_grpc import FloraRenderingProblemServiceStub


ENERGY_SIGNAL = 'nvmlDeviceGetTotalEnergyConsumption'


class FloraRenderingClient:
    def __init__(self, addr):
        self.stub = FloraRenderingProblemServiceStub(
            grpc.insecure_channel(addr))

    def next_configuration(self):
        return self.stub.NextConfiguration(Empty())

    def evaluate(self, energy, runtime, piqe, mse):
        score = RenderingScore()
        score.energy = energy
        score.runtime = runtime
        score.piqe = piqe
        score.mse = mse
        return self.stub.Evaluate(score)


def get_filter_cycles(filter_kind, x, y):
    if filter_kind == 'BOX':
        return 1
    elif filter_kind == 'GAUSSIAN':
        return x * y
    elif filter_kind == 'BLACKMAN_HARRIS':
        return 1


def get_score(config, pixels):
    return {
        'energy': config.resolution_x * config.resolution_y * sqrt(pixels),
        'runtime': pixels,
        'piqe': 1 / pixels,
        'mse': config.resolution_x * config.resolution_y / sqrt(pixels),
    }


def main():
    client = FloraRenderingClient('localhost:8980')
    scores = []
    for i in range(500):
        config = client.next_configuration()
        print(f'trying configuration {config}')
        pixels = 0
        for _ in range(config.resolution_x):
            for _ in range(config.resolution_y):
                pixels += config.aa_min**2
                pixels += config.aa_max**2
                pixels += config.ao_samples**2
                pixels += get_filter_cycles(
                    config.filter,
                    config.resolution_x,
                    config.resolution_y
                )
        score = get_score(config, pixels)
        print(f'configuration scored {score}')
        scores.append({
            'iteration': i,
            'configuration': MessageToDict(config),
            'results': score
        })
        client.evaluate(**score)
    json.dump(scores, open('/tmp/results.json', 'w'))


if __name__ == '__main__':
    main()
