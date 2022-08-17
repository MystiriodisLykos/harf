from dataclasses import dataclass
from typing import Union, Dict, List, TypeVar, Callable, Tuple, Protocol, Generic
import json
import re

A = TypeVar("A")
B = TypeVar("B")
P = TypeVar("P")

JsonPrims = Union[int, float, str, bool, None]
JsonF = Union[Dict[str, A], List[A], JsonPrims]

Json = JsonF["Json"]


def jsonf_fmap(f: Callable[[A], B], j: JsonF[A]) -> JsonF[B]:
    if isinstance(j, dict):
        return {k: f(v) for k, v in j.items()}
    if isinstance(j, list):
        return [f(e) for e in j]
    return j


def jsonf_cata(a: Callable[[JsonF[A]], A], j: Json) -> A:
    def inner(e):
        return jsonf_cata(a, e)

    return a(jsonf_fmap(inner, j))
