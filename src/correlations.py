from dataclasses import dataclass, field
from functools import partial
from typing import Set, NamedTuple, Iterable, Any, List, NewType, Union, Protocol
from urllib.parse import urlparse
from itertools import chain
import json

from serde.json import from_json

from harf import cata, Har, HarF, PostDataTextF, QueryStringF, ContentF, RequestF, ResponseF, EntryF, LogF, TopF


class Correlation(NamedTuple):
    value: Any
    names: Set[str]

    def __hash__(self):
        return hash(self.value)


class Path(Protocol):
    next_: "Path"


@dataclass
class EndPath:
    next_: None = field(init=False, default=None)

    def __str__(self):
        return ""


@dataclass
class IntPath:
    index: int
    next_: "DataPath" = EndPath()

    def __str__(self):
        return f"[{self.index}]{self.next_}"


@dataclass
class StrPath:
    name: str
    next_: "DataPath" = EndPath()

    def __str__(self):
        return f".{self.name}{self.next_}"


DataPath = Union[IntPath, StrPath, EndPath]


class UrlPath(IntPath):
    def __str__(self):
        return f".url{super().__str__()}"


class QueryPath(StrPath):
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
        return f".response{self.next_}"


@dataclass
class EntryPath:
    index: int
    next_: Union[RequestPath, ResponsePath]

    def __str__(self):
        return f"[{self.index}]{self.next_}"


def json_paths(element) -> List[Path]:
    if isinstance(element, dict):
        iter_ = element.items()
        path = StrPath
    elif isinstance(element, list):
        iter_ = enumerate(element)
        path = IntPath
    else:
        return [EndPath()]
    return [path(k, p) for k, v in iter_ for p in json_paths(v)]


def paths(element: HarF[List[Path]]) -> List[Path]:
    if isinstance(element, PostDataTextF):
        return [RequestPath(BodyPath(r)) for r in json_paths(json.loads(element.text))]
    if isinstance(element, RequestF):
        path = urlparse(element.url).path.strip("/").split("/")
        paths = []
        for i in range(len(path)):
            paths.append(RequestPath(UrlPath(i)))
        return paths + (element.postData or [])
    if isinstance(element, ContentF):
        return [ResponsePath(p) for p in (json_paths(json.loads(element.text)) if element.text else [])]
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

#def correlations(element: HarF[Set[Correlation]) -> Set[Correlation]:
#    if isinstance(element, RequestF):
#        return set()
#    if isinstance(element, EntryF):
#        return element.request
#    if isinstance(elment, LogF):
#        return element.entries[0]
#    if isinstance(element, TopF):
#        return element.log
#    return set()


from pprint import pprint

with open("test/example1.har") as file:
    har = from_json(Har, file.read())
    paths_ = cata(paths, har)
    pprint(paths_)
    for p in paths_:
        print(p)
