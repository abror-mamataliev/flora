""" a thin client to talk to a flora server. """
from math import sqrt

from collector import DataCollector
from flora_client import FloraRenderingProbemClient


def get_filter_cycles(filter_kind, x, y):
    if filter_kind == 'BOX':
        return 1
    elif filter_kind == 'GAUSSIAN':
        return x * y
    elif filter_kind == 'BLACKMAN_HARRIS':
        return 1


def get_scores(config, pixels):
    return {
        'energy': config.resolution_x * config.resolution_y * sqrt(pixels),
        'runtime': pixels,
        'piqe': 1 / pixels,
        'mse': config.resolution_x * config.resolution_y / sqrt(pixels),
    }


def main():
    client = FloraRenderingProbemClient('localhost:8980')
    data_collector = DataCollector()
    for i in range(500):
        config = client.next_configuration()
        print(f'trying configuration {config}')
        pixels = 0
        for _ in range(config.resolution_x):
            for _ in range(config.resolution_y):
                pixels += config.aa_samples**2
                pixels += config.ao_samples**2
                pixels += get_filter_cycles(
                    config.filter,
                    config.resolution_x,
                    config.resolution_y
                )
        scores = get_scores(config, pixels)
        print(f'configuration scored {scores}')
        data_collector.add_record(i, config, scores)
        client.evaluate(**scores)
    data_collector.write_data('/tmp/results.json')


if __name__ == '__main__':
    main()
