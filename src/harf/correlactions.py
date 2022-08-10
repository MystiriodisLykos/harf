from collections import defaultdict
from dataclasses import dataclass, field
from functools import partial
from typing import (
    Set,
    NamedTuple,
    Iterable,
    Any,
    List,
    NewType,
    Union,
    Protocol,
    Dict,
    TypeVar,
    Callable,
    Tuple,
    Set,
    Generic,
)
from urllib.parse import urlparse
from itertools import chain
import json

from serde.json import from_json

from harf import (
    cata,
    Har,
    HarF,
    PostDataTextF,
    QueryStringF,
    ContentF,
    RequestF,
    ResponseF,
    EntryF,
    LogF,
    TopF,
)
from jsonf import jsonf_cata, JsonF, JsonPrims

A = TypeVar("A")
B = TypeVar("B")


class Path(Protocol):
    next_: "Path"


@dataclass
class IntPath(Generic[A]):
    index: int
    next_: A

    def __str__(self):
        return f"[{self.index}]{self.next_}"


@dataclass
class StrPath(Generic[A]):
    key: str
    next_: A

    def __str__(self):
        return f".{self.key}{self.next_}"


@dataclass
class EndPath:
    def __str__(self):
        return ""


DataPath = Union[IntPath[A], StrPath[A], EndPath]["DataPath"]  # type: ignore[index]


class UrlPath(IntPath[DataPath]):
    def __str__(self):
        return f".url{super().__str__()}"


class QueryPath(StrPath[DataPath]):
    def __str__(self):
        return f".queryString{super().__str__()}"


@dataclass
class BodyPath:
    next_: DataPath

    def __str__(self):
        return f".body{self.next_}"


@dataclass
class RequestPath:
    next_: Union[UrlPath, QueryPath, BodyPath]

    def __str__(self):
        return f".request{self.next_}"


class ResponsePath(BodyPath):
    def __str__(self):
        return f".response{super().__str__()}"


@dataclass
class EntryPath:
    index: int
    next_: Union[RequestPath, ResponsePath]

    def __str__(self):
        return f"entry_{self.index}{self.next_}"

Env = Dict[JsonPrims, List[Path]]

class Env(Dict[JsonPrims, List[Path]]):
    def map_paths(self, f: Callable[[Path], Path]) -> "Env":
        res = {}
        for p, ps in self.items():
            res[p] = list(map(f, ps))
        return Env(res)

def _json_env(element: JsonF[Env]) -> Env:
    if isinstance(element, dict):
        iter_ = element.items()
        mk_path = StrPath
    elif isinstance(element, list):
        iter_ = enumerate(element)
        mk_path = IntPath
    else:
        return Env({element: [EndPath()]})
    res = defaultdict(list)
    for path, envs in iter_:
        for prim, paths in envs.items():
           res[prim] += [mk_path(path, p) for p in paths]
    return Env(res)


json_env = partial(jsonf_cata, _json_env)


def env(element: HarF[Env]) -> Env:
    if isinstance(element, PostDataTextF):
        return json_env(json.loads(element.text)).map_paths(lambda p: RequestPath(BodyPath(p)))
    if isinstance(element, RequestF):
        url_path = urlparse(element.url).path.strip("/").split("/")
        request_env = element.postData or Env()
        for i, p in enumerate(url_path):
            path = [RequestPath(UrlPath(i, EndPath()))]
            if p.isdigit():
                p = int(p)
            if p in request_env:
                request_env[p] = path + request_env[p]
            else:
                request_env[p] = path
        return request_env
    if isinstance(element, ContentF):
        content = element.text
        if content != "":
            content_env = json_env(json.loads(element.text))
        else:
            content_env = Env()
        return content_env.map_paths(lambda p: ResponsePath(p))
    if isinstance(element, ResponseF):
        return element.content
    if isinstance(element, EntryF):
        entry_env = element.request
        for prim, paths in element.response.items():
            if prim in entry_env:
                entry_env[prim] += paths
            else:
                entry_env[prim] = paths
        return entry_env
    if isinstance(element, LogF):
        log_env = defaultdict(list)
        for i, entry in enumerate(element.entries):
            for prim, paths in entry.items():
                log_env[prim] += [EntryPath(i, p) for p in paths]
        return Env(log_env)
    if isinstance(element, TopF):
        return element.log
    return Env()


from pprint import pprint

with open("test/example1.har") as file:
    har = from_json(Har, file.read())
    env_ = cata(env, har)
    pprint(env_)
    for prim, paths in env_.items():
        print(prim)
        pprint(list(map(str, paths)))
        print()

import code

# code.interact(local=vars())
