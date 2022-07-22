from dataclasses import dataclass
from functools import partial
from typing import Set, NamedTuple, Iterable, Any, List, NewType, Union, Protocol
from urllib.parse import urlparse
from itertools import chain

from serde.json import from_json

from harf import cata, Har, HarF, QueryStringF, RequestF, EntryF, LogF, TopF

class Correlation(NamedTuple):
    value: Any
    names: Set[str]

    def __hash__(self):
        return hash(self.value)

class Path(Protocol):
    next_: "Path"

@dataclass
class IntPath:
    index: int
    next_: "DataPath"

@dataclass
class StrPath:
    name: str
    next_: "DataPath"

DataPath = Union[IntPath, StrPath, None]

class UrlPath(IntPath): pass
class QueryPath(StrPath): pass

@dataclass
class BodyPath:
    next_: DataPath

@dataclass
class RequestPath:
    next_: Union[UrlPath, QueryPath, BodyPath]

class ResponsePath(BodyPath): pass

@dataclass
class EntryPath:
   index: int
   next_: Union[RequestPath, ResponsePath]

def paths(element: HarF[List[Path]]) -> List[Path]:
    if isinstance(element, RequestF):
        path = urlparse(element.url).path.strip("/").split("/")
        paths = []
        for i in range(len(path)):
            paths.append(RequestPath(UrlPath(i, None)))
        return paths
    if isinstance(element, EntryF):
        return element.request
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
    pprint(cata(paths, har))
