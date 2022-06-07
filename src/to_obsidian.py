from serde.json import from_json

from harf import cata, Har, QueryStringF, HeaderF, RequestF, EntryF, LogF, TopF, HarF
from typing import Any, NamedTuple

with open("test/www.demoblaze.com_Archive [22-05-30 13-47-04].har") as file:
    data = from_json(Har, file.read())


class EnvE(NamedTuple):
    name: str
    value: Any

Env = List[EnvE]

def get_values(element: HarF[Tuple[HarF, Env]]) -> Tuple[HarF, Env]:
#    match type(element):
#        case QueryStringF:
    if isinstance(element, QueryStringF):
            id = uuid4()
            name, value = element.name, element.value
            return replace(element, name=id), [EnvE(id, value), EnvE(name, value)]
#        case HeaderF:
#    if isinstance(element, HeaderF):
#            id = uuid4()
#            name, value = element.name, element.value
#            return replace(element, name=id), [EnvE(id, value), EnvE(name, value)]
#        case RequestF:
    if isinstance(element, RequestF):
            env = [EnvE("Path", element.url.split("?")[0])]
            for q in element.queryString:
                env += q[1]
            return element, env
#        case EntryF:
    if isinstance(element, EntryF):
            return element, element.request[1]
#        case LogF:
    if isinstance(element, LogF):
            env = element.entries[-1][1]
            for e in reversed(element.entries[:-1]):
                env += e[1]
            return element, env
#        case TopF:
    if isinstance(element, TopF):
            return element, element.log
    return element, []


print(data.log.entries[2])
