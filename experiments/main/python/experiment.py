import logging
import sys
from argparse import ArgumentParser
from pathlib import Path

import bpy
from grpc._channel import _InactiveRpcError
from pyRAPL import setup as rapl_setup
from pynvml import nvmlInit, nvmlShutdown

from blender import BlenderSceneRenderer
from collector import DataCollector
from flora_client import FloraRenderingProblemClient
from flora_rendering_problem_service_pb2 import RenderingConfiguration, RenderingScore
from meter import MultiMeter

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    stream=sys.stdout,
    force=True
)

TEST_CONFIGURATION = RenderingConfiguration(
    resolution_x=100,
    resolution_y=100,
    aa_samples=0,
    ao_samples=0,
    filter="GAUSSIAN",
    threads=1
)


class Experiment:
    def __init__(self, scene: Path, output_dir: Path, device: str, ec_port: int):
        self.scene_file = scene
        self.scene_name = scene.stem
        self.output_dir = output_dir
        self.device = device

        bpy.ops.wm.open_mainfile(filepath=self.scene_file.as_posix())
        self.scene_renderer = BlenderSceneRenderer(scene=bpy.context.scene)
        self.scene_renderer.set_render_settings(device=self.device)

        self.client = FloraRenderingProblemClient(f"localhost:{ec_port}")
        self.multi_meter = MultiMeter(self.image_source)
        self.data_collector = DataCollector()

        self.image_reference = None

    def image_source(self):
        return self.image_reference

    def warmup(self):
        self.scene_renderer.apply_configuration(TEST_CONFIGURATION, warmup=True)
        self.multi_meter.start()
        self.scene_renderer.render()
        self.image_reference = "/tmp/warmup.png"
        self.multi_meter.stop()

    def run(self, num_iterations: int | None = None):
        i = 0
        while num_iterations is None or i < num_iterations:
            try:
                config = self.client.next_configuration()
            except _InactiveRpcError as e:
                logging.error("Flora client is inactive.")
                break

            output_file = self.output_dir / f"{self.scene_name}-{i}.png"
            self.scene_renderer.apply_configuration(
                config,
                output_file_path=output_file.as_posix()
            )

            self.multi_meter.start()
            self.scene_renderer.render()
            self.image_reference = output_file.as_posix()
            self.multi_meter.stop()
            
            scores = self.multi_meter.read()
            logging.info(f"Scores {RenderingScore(**scores)}")
            self.client.evaluate(**scores)
            self.data_collector.add_record(i, config, scores)
            i += 1

    def save_results(self):
        results_file = self.output_dir / "results.json"
        self.data_collector.write_data(results_file.as_posix())
        logging.info(f"Results saved to {results_file.as_posix()}")

    def cleanup(self):
        self.scene_renderer.cleanup()


def parse_args():
    parser = ArgumentParser()
    parser.add_argument(
        "-s",
        "--scene",
        help="path to blender scene file to render",
        type=str,
        required=True,
    )
    parser.add_argument(
        "-p", "--port", help="port for the EC server", type=int, default=8980
    )
    parser.add_argument(
        "-d", "--device", help="device to render with", type=str, default=""
    )
    parser.add_argument(
        "-o",
        "--output",
        help="directory to save rendered images",
        type=str,
        default="rendering-data",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    args.scene = Path(args.scene)
    args.output = Path(args.output)
    args.output.mkdir(parents=True, exist_ok=True)

    rapl_setup()
    nvmlInit()

    experiment = Experiment(
        scene=args.scene, output_dir=args.output,
        device=args.device, ec_port=args.port
    )
    experiment.warmup()
    experiment.run()
    experiment.save_results()
    experiment.cleanup()

    nvmlShutdown()


if __name__ == "__main__":
    main()
