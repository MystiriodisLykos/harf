from dataclasses import dataclass
from typing import Union, Dict, List, TypeVar, Callable, Tuple, Protocol, Generic

A = TypeVar("A")
B = TypeVar("B")
P = TypeVar("P")

JSONF = Union[Dict[str, A], List[A], int, str, bool, float, None]
JSON = JSONF["JSON"]

@dataclass
class IntPath(Generic[P]):
    index: int
    next_: P
    def __str__(self):
        return f"[{self.index}]{self.next_}"

@dataclass
class StrPath(Generic[P]):
    key: str
    next_: P
    def __str__(self):
        return f".{self.key}{self.next_}"

@dataclass
class EndPath(Generic[P]):
    @property
    def next_(self) -> "PathP":
        return self
    def __str__(self):
        return ""

JsonPath = Union[IntPath[P], StrPath[P], EndPath[P]]["JsonPath"]

Env = Dict[str, List[JsonPath]]

def jsonf_fmap(f: Callable[[A], B], j: JSONF[A]) -> JSONF[B]:
    if isinstance(j, dict):
        return {k: f(v) for k, v in j.items()}
    if isinstance(j, list):
        return [f(e) for e in j]
    return j

def jsonf_cata(a: Callable[[JSONF[A]], A], j: JSON) -> A:
    def inner(e):
        return jsonf_cata(a, e)
    return a(jsonf_fmap(inner, j))

def jsonf_para(a: Callable[[JSONF[Tuple[JSON, A]]], A], j: JSON) -> A:
    def inner(e):
        return jsonf_fmap(lambda x: x[0], e), a(e)
    return jsonf_cata(inner, j)[1]

def jsonf_zygo(h: Callable[[JSONF[B]], B], a: Callable[[JSONF[Tuple[B, A]]], A], j: JSON) -> A:
    def inner(e):
        return h(jsonf_fmap(lambda e: e[0], e)), a(e)
    return jsonf_cata(inner, j)[1]

def json_paths(j: JSONF[List[str]]) -> List[str]:
    if isinstance(j, dict):
        iter_ = j.items()
    elif isinstance(j, list):
        iter_ = enumerate(j)
    else:
        return [""]
    res = []
    for p, ns in iter_:
        s = [str(p) + p_ for p_ in ns]
        res += s
    return res

def json_env(j: JSONF[Env]) -> Env:
    """ What function do I need to turn json_paths into this?
    json_paths :: JsonF [String] -> [String]
    json_correlations :: JsonF {Prim, [String]} -> {Prim, [String]}
    _ :: Prim -> [String] -> {Prim, [String]}
      :: b -> a -> {b, a}
    """
    if isinstance(j, dict):
        iter_ = j.items()
        path = StrPath
    elif isinstance(j, list):
        iter_ = enumerate(j)
        path = IntPath
    else:
        return {j: [EndPath()]}
    res = {}
    for p, d in iter_:
        for k, v in d.items():
            u = [path(p, p_) for p_ in v]
            if k in res:
                res[k] += u
            else:
                res[k] = u
    return res

example = {
    "a" : 1,
    "bs": [2, 3],
    "cs": [4, 6],
    "ds": [
        {"x": 7},
        {"y": 1}
    ]
}
l = {"a": [1,2,3], "b": [2,4,6]}
print(l)
env = jsonf_cata(json_env, l)
for v, p in env.items():
    print(v, [str(p_) for p_ in p])
