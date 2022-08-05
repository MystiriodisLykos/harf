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


class StrList(list):
    def __str__(self):
        return "[" + ", ".join(str(e) for e in self) + "]"


class StrDict(dict):
    def __str__(self):
        return "{" + ", ".join(f"{k}: {str(v)}" for k, v in self.items()) + "}"


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
    def next_(self) -> "EndPath":
        return self

    def __str__(self):
        return ""


JsonPath = Union[IntPath[P], StrPath[P], EndPath[P]]["JsonPath"]

JsonEnv = Dict[JsonPrims, List[JsonPath]]


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


def json_env(j: JsonF[JsonEnv]) -> JsonEnv:
    if isinstance(j, dict):
        iter_ = j.items()
        path = StrPath
    elif isinstance(j, list):
        iter_ = enumerate(j)
        path = IntPath
    else:
        return {j: StrList([EndPath()])}
    res = StrDict()
    for p, d in iter_:
        for k, v in d.items():
            u = StrList([path(p, p_) for p_ in v])
            if k in res:
                res[k] += u
            else:
                res[k] = u
    return res


def replace_with_obsidian_links(env: JsonEnv, j: JsonF[Json]) -> Json:
    if isinstance(j, dict):
        return j
    if isinstance(j, list):
        return j
    return f"[[{env[j][0]}|{j}]]"


def to_obsidian(j: Json) -> str:
    env = jsonf_cata(json_env, j)

    def replace(j):
        return replace_with_obsidian_links(env, j)

    replaced = jsonf_cata(replace, j)
    formatted = json.dumps(replaced, indent=4)
    formatted = re.sub(r"^(\s*)(\S)", r"\1- \2", formatted, flags=re.MULTILINE)
    return re.sub(r"- ([\[\]\{\}])", r"- \\\1", formatted)
