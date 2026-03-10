import knob_pb2 as _knob_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Empty(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class RenderingKnobs(_message.Message):
    __slots__ = ("resolutionX", "resolutionY", "antiAliasMin", "antiAliasMax", "ambientOcclusionSamples", "filter")
    RESOLUTIONX_FIELD_NUMBER: _ClassVar[int]
    RESOLUTIONY_FIELD_NUMBER: _ClassVar[int]
    ANTIALIASMIN_FIELD_NUMBER: _ClassVar[int]
    ANTIALIASMAX_FIELD_NUMBER: _ClassVar[int]
    AMBIENTOCCLUSIONSAMPLES_FIELD_NUMBER: _ClassVar[int]
    FILTER_FIELD_NUMBER: _ClassVar[int]
    resolutionX: _knob_pb2.RangeKnob
    resolutionY: _knob_pb2.RangeKnob
    antiAliasMin: _knob_pb2.RangeKnob
    antiAliasMax: _knob_pb2.RangeKnob
    ambientOcclusionSamples: _knob_pb2.RangeKnob
    filter: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, resolutionX: _Optional[_Union[_knob_pb2.RangeKnob, _Mapping]] = ..., resolutionY: _Optional[_Union[_knob_pb2.RangeKnob, _Mapping]] = ..., antiAliasMin: _Optional[_Union[_knob_pb2.RangeKnob, _Mapping]] = ..., antiAliasMax: _Optional[_Union[_knob_pb2.RangeKnob, _Mapping]] = ..., ambientOcclusionSamples: _Optional[_Union[_knob_pb2.RangeKnob, _Mapping]] = ..., filter: _Optional[_Iterable[str]] = ...) -> None: ...

class RenderingConfiguration(_message.Message):
    __slots__ = ("resolutionX", "resolutionY", "antiAliasMin", "antiAliasMax", "ambientOcclusionSamples", "filter")
    RESOLUTIONX_FIELD_NUMBER: _ClassVar[int]
    RESOLUTIONY_FIELD_NUMBER: _ClassVar[int]
    ANTIALIASMIN_FIELD_NUMBER: _ClassVar[int]
    ANTIALIASMAX_FIELD_NUMBER: _ClassVar[int]
    AMBIENTOCCLUSIONSAMPLES_FIELD_NUMBER: _ClassVar[int]
    FILTER_FIELD_NUMBER: _ClassVar[int]
    resolutionX: int
    resolutionY: int
    antiAliasMin: int
    antiAliasMax: int
    ambientOcclusionSamples: int
    filter: str
    def __init__(self, resolutionX: _Optional[int] = ..., resolutionY: _Optional[int] = ..., antiAliasMin: _Optional[int] = ..., antiAliasMax: _Optional[int] = ..., ambientOcclusionSamples: _Optional[int] = ..., filter: _Optional[str] = ...) -> None: ...

class RenderingScore(_message.Message):
    __slots__ = ("energy", "runtime", "mse", "piqe")
    ENERGY_FIELD_NUMBER: _ClassVar[int]
    RUNTIME_FIELD_NUMBER: _ClassVar[int]
    MSE_FIELD_NUMBER: _ClassVar[int]
    PIQE_FIELD_NUMBER: _ClassVar[int]
    energy: float
    runtime: float
    mse: float
    piqe: float
    def __init__(self, energy: _Optional[float] = ..., runtime: _Optional[float] = ..., mse: _Optional[float] = ..., piqe: _Optional[float] = ...) -> None: ...
