from functools import partial
from typing import Callable, TypeVar, Any, Tuple

A = TypeVar("A")
B = TypeVar("B")
C = TypeVar("C")
S = TypeVar("S")
T = TypeVar("T")

FMAP = Callable[[Callable[[A], B], S], T]

def cata(fmap: FMAP[A, B, S, T], alg: Callable[[T], A], source: S) -> A:
    """
    fmap :: (a -> b) -> s   -> t
    fmap :: (a -> b) -> s a -> s b
    alg :: t   -> a
    alg :: s b - > a
    source :: s
    """
    inner_cata = partial(cata, fmap, alg)
    results = fmap(inner_cata, source)
    return alg(results)


def para(fmap: FMAP[A, B, S, T], alg: Callable[[S, T], A], source: S) -> A:
    def alg_(x):
        source = fmap(lambda p: p[0], x)
        results = fmap(lambda p: p[1], x)
        result = alg(source, results)
        return (source, result)
    return cata(fmap, alg_, source)[1]


from enum import Enum

class BoolF(Enum):
    F = 0
    T = 1

def fmap_bool(f: Any, b: BoolF) -> BoolF:
    return b

def boolF(T: A, F: A, b: BoolF) -> A:
    def alg(b: BoolF) -> A:
        if b == BoolF.T:
            return T
        return F
    return cata(fmap_bool, alg, b)


def fmap_json(f: Any, j):
    if type(j) == list:
        return [f(e) for e in j]
    if type(j) == dict:
        return {k: f(v) for k, v in j.items()}
    return j


from dataclasses import dataclass, is_dataclass, replace
from typing import List, Optional, Union

@dataclass
class Sub:
    x: int
    y: Optional[str]

@dataclass
class Nest:
    a: List[Sub]

def lifted_fmap_dataclass(f: Any, d):
    if is_dataclass(d):
        fields_ = fields(d)
        new_values = {}
        for field in fields_:
            name = field.name
            value = getattr(d, name)
            if type(value) in set([list, tuple, dict, set]):
                new_values[name] = lifted_fmap_dataclass(f, value)
            else:
                new_values[name] = f(value)
        return replace(d, **new_values)
    if type(d) == list:
        return [f(e) for e in d]
    if type(d) == tuple:
        return (f(e) for e in d)
    if type(d) == dict:
        return {k: f(v) for k, v in d.items()}
    if type(d) == set:
        return {f(e) for e in d}
    return d
