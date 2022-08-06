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
from jsonf import jsonf_cata, JsonF

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


DataPath = Union[IntPath[A], StrPath[A], EndPath]["DataPath"]  # type: ignore[misc]


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
        return f"[{self.index}]{self.next_}"


def json_path(element: JsonF[List[DataPath]]) -> List[DataPath]:
    if isinstance(element, dict):
        iter_ = element.items()
        path = StrPath
    elif isinstance(element, list):
        iter_ = enumerate(element)
        path = IntPath
    else:
        return [EndPath()]
    res = []
    for p, v in iter_:
        res += [path(p, p_) for p_ in v]
    return res


json_paths = partial(jsonf_cata, json_path)


def paths(element: HarF[List[Path]]) -> List[Path]:
    if isinstance(element, PostDataTextF):
        return [RequestPath(BodyPath(r)) for r in json_paths(json.loads(element.text))]
    if isinstance(element, RequestF):
        path = urlparse(element.url).path.strip("/").split("/")
        paths = []
        for i in range(len(path)):
            paths.append(RequestPath(UrlPath(i, EndPath())))
        return paths + (element.postData or [])
    if isinstance(element, ContentF):
        return [
            ResponsePath(p)
            for p in (json_paths(json.loads(element.text)) if element.text else [])
        ]
    if isinstance(element, ResponseF):
        return element.content
    if isinstance(element, EntryF):
        return element.request + element.response
    if isinstance(element, LogF):
        results = []
        for i, entry in enumerate(element.entries):
            results.extend(map(lambda e: EntryPath(i, e), entry))
        return results
    if isinstance(element, TopF):
        return element.log
    return []


from pprint import pprint

with open("test/example1.har") as file:
    har = from_json(Har, file.read())
    paths_ = cata(paths, har)
    pprint(paths_)
    for p in paths_:
        print(p)
