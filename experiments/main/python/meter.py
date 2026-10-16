import logging
from abc import ABC
from time import time

import numpy as np
from brisque import BRISQUE
from PIL import Image
from pynvml import (
    nvmlDeviceGetCount, nvmlDeviceGetHandleByIndex,
    nvmlDeviceGetTotalEnergyConsumption
)
from pypiqe import piqe
from pyRAPL import Measurement


class Meter(ABC):
    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def read(self) -> dict[str, float]:
        raise NotImplementedError("Subclasses must implement this method.")


class TimeMeter(Meter):
    def start(self) -> None:
        self.start_time = time()

    def stop(self) -> None:
        self.end_time = time()

    def read(self) -> dict[str, float]:
        return {"runtime": self.end_time - self.start_time}


class RaplEnergyMeter(Meter):
    def __init__(self):
        self.measure = Measurement("measure")

    def start(self) -> None:
        self.measure.begin()

    def stop(self) -> None:
        self.measure.end()

    def read(self) -> dict[str, float]:
        result = self.measure.result
        if result.pkg is None:
            logging.info("RAPL energy measurement is not available on this system.")
            pkg_energy = 0
        else:
            pkg_energy = sum(result.pkg)

        if result.dram is None:
            logging.info("DRAM energy measurement is not available on this system.")
            dram_energy = 0
        else:
            dram_energy = sum(result.dram)
        
        energy_uj = pkg_energy + dram_energy
        return {"cpu_energy": energy_uj / 1e6}


class NvmlEnergyMeter(Meter):
    def __init__(self):
        self.device_count = nvmlDeviceGetCount()
        self.devices = [nvmlDeviceGetHandleByIndex(i) for i in range(self.device_count)]
        self.energies = {}

    def start(self) -> None:
        for device_index in range(self.device_count):
            self.energies[device_index] = nvmlDeviceGetTotalEnergyConsumption(self.devices[device_index])

    def stop(self) -> None:
        for device_index in range(self.device_count):
            self.energies[device_index] = nvmlDeviceGetTotalEnergyConsumption(
                self.devices[device_index]
            ) - self.energies[device_index]

    def read(self) -> dict[str, float]:
        return {"gpu_energy": sum(self.energies.values()) / 1e3}


class EnergyMeter(Meter):
    def __init__(self):
        self.meters = [
            RaplEnergyMeter(),
            NvmlEnergyMeter()
        ]

    def start(self) -> None:
        for meter in self.meters:
            meter.start()

    def stop(self) -> None:
        for meter in self.meters:
            meter.stop()

    def read(self) -> dict[str, float]:
        return {"energy": sum(value for meter in self.meters for value in meter.read().values())}


class ImageMeter(Meter):
    def __init__(self, image_source: callable):
        self.image_source = image_source

    def start(self) -> None:
        pass

    def stop(self) -> None:
        image_path = self.image_source()
        img = Image.open(image_path).resize((1200, 1200)).convert("RGB")
        self.img = np.array(img)


class PiqeMeter(ImageMeter):
    def __init__(self, image_path: str):
        super().__init__(image_path)

    def read(self) -> dict[str, float]:
        return {"piqe": piqe(self.img)[0]}


class BrisqueMeter(ImageMeter):
    def __init__(self, image_path: str):
        super().__init__(image_path)


    def read(self) -> dict[str, float]:
        return {"brisque": BRISQUE(url=False).score(self.img)}


class MultiMeter(Meter):
    def __init__(self, image_source: callable):
        self.image_source = image_source
        self.meters = [
            RaplEnergyMeter(),
            NvmlEnergyMeter(),
            EnergyMeter(),
            TimeMeter(),
            PiqeMeter(image_source),
            BrisqueMeter(image_source)
        ]

    def start(self) -> None:
        for meter in self.meters:
            meter.start()

    def stop(self) -> None:
        for meter in self.meters:
            meter.stop()

    def read(self) -> dict[str, float]:
        return {
            key: value for meter in self.meters for key, value in meter.read().items()
        }
