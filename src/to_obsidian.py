from serde.json import from_json

from harf import cata, Har, QueryStringF, HeaderF, RequestF, EntryF, LogF, TopF, HarF
from typing import Any, NamedTuple

with open("test/www.demoblaze.com_Archive [22-05-30 13-47-04].har") as file:
    data = from_json(Har, file.read())


class Env(NamedTuple):
    name: str
    value: Any
    next_: "Env"


def get_values(element: HarF[Env]) -> Env:
#    match type(element):
#        case QueryStringF:
    if isinstance(element, QueryStringF):
            return Env(element.name, element.value, None)
#        case HeaderF:
    if isinstance(element, HeaderF):
            return Env(element.name, element.value, None)
#        case RequestF:
    if isinstance(element, RequestF):
            env = Env("Path", element.url.split("?")[0], None)
#            for h in element.headers[1:]:
#                env = Env(h.name, h.value, env)
            for q in element.queryString:
                env = Env(q.name, q.value, env)
            return env
#        case EntryF:
    if isinstance(element, EntryF):
            return element.request
#        case LogF:
    if isinstance(element, LogF):
            env = element.entries[-1]
            for e in reversed(element.entries[:-1]):
                env = Env(e.name, e.value, env)
            return env
#        case TopF:
    if isinstance(element, TopF):
            return element.log
    return None


print(data.log.entries[2])
