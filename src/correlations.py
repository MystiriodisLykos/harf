from typing import Set, NamedTuple, Iterable, Any, List
from urllib.parse import urlparse
from itertools import chain

from serde.json import from_json

from harf import cata, Har, HarF, QueryStringF, RequestF, EntryF, LogF, TopF

class Correlation(NamedTuple):
    value: Any
    names: Set[str]

    def __hash__(self):
        return hash(self.value)

def names(element: HarF[List[str]]) -> List[str]:
    if isinstance(element, RequestF):
        path = urlparse(element.url).path.strip("/").split("/")
        path_names = []
        for i, part in enumerate(path):
            path_names.append(f"path[{i}]")
        return path_names
    if isinstance(element, EntryF):
        return ["request"] + list(map(lambda e: f"request.{e}", element.request))
    if isinstance(element, LogF):
        results = []
        for i, entry in enumerate(element.entries):
            for name in entry:
                results.append(f"[{i}]{name}")
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
    pprint(cata(names, har))
