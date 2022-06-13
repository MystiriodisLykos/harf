from serde.json import from_json

from collections.abc import Mapping, Iterable
from dataclasses import replace, is_dataclass, fields
from harf import cata, Har, QueryStringF, HeaderF, RequestF, ResponseF, EntryF, LogF, TopF, HarF, PostDataTextF
from typing import Any, NamedTuple, Tuple, List, TypeVar, Generic, Callable
from uuid import uuid4
from urllib.parse import urlparse

A = TypeVar("A")
S = TypeVar("S")
R = TypeVar("R")

def pretty_print(obj, indent=4):
    """
    Pretty prints a (possibly deeply-nested) dataclass.
    Each new block will be indented by `indent` spaces (default is 4).
    """
    print(stringify(obj, indent))

def stringify(obj, indent=4, _indents=0):
    if isinstance(obj, str):
        return f"'{obj}'"

    if not is_dataclass(obj) and not isinstance(obj, (Mapping, Iterable)):
        return str(obj)

    this_indent = indent * _indents * ' '
    next_indent = indent * (_indents + 1) * ' '
    start, end = f'{type(obj).__name__}(', ')'  # dicts, lists, and tuples will re-assign this

    if is_dataclass(obj):
        body = '\n'.join(
            f'{next_indent}{field.name}='
            f'{stringify(getattr(obj, field.name), indent, _indents + 1)},' for field in fields(obj)
        )

    elif isinstance(obj, Mapping):
        if isinstance(obj, dict):
            start, end = '{}'

        body = '\n'.join(
            f'{next_indent}{stringify(key, indent, _indents + 1)}: '
            f'{stringify(value, indent, _indents + 1)},' for key, value in obj.items()
        )

    else:  # is Iterable
        if isinstance(obj, list):
            start, end = '[]'
        elif isinstance(obj, tuple):
            start = '('

        body = '\n'.join(
            f'{next_indent}{stringify(item, indent, _indents + 1)},' for item in obj
        )

    return f'{start}\n{body}\n{this_indent}{end}'


def json_cata(algebra: Callable[[A], R], source: S) -> R:
    def inner(element):
        return json_cata(algebra, element)
    if isinstance(source, list):
        results = [inner(e) for e in source]
    elif isinstance(source, dict):
        results = {k: inner(e) for k, e in source.items()}
    else:
        results = source
    return algebra(results)



class Thunk(Generic[A]):
    _thunk_indices = []
    _thunk_values = []
    def __new__(cls, value: A):
        try:
            thunk_index = cls._thunk_indices.index(value)
            return cls._thunk_values[thunk_index]
        except ValueError:
            thunk = super().__new__(cls)
            cls._thunk_indices.append(value)
            cls._thunk_values.append(thunk)
            return thunk
    def __init__(self, value: A):
        self._value = value
    def __eq__(self, other):
        return self._value == other._value
    def __repr__(self):
        return f"Thunk({self._value!r})"

class EnvE(NamedTuple):
    name: str
    value: Thunk[Any]

Env = List[EnvE]


def json_env(json) -> Env:
    if isinstance(json, list):
        iterator = map(lambda e: (f"[{len(json)-e[0]-1}]", e[1]), enumerate(reversed(json)))
    elif isinstance(json, dict):
        iterator = map(lambda e: (f".{e[0]}", e[1]), reversed(json.items()))
    else:
        return [EnvE("", Thunk(json))]
    env = []
    for k, v in iterator:
        sub_env = list(map(lambda e: EnvE(k + e.name, e.value), v))
        env += sub_env
    return EnvE("", Thunk(json)) + env

def build_env(element: HarF[Env]) -> Env:
    if isinstance(element, PostDataTextF):
        return json_cata(json_env, element)
    if isinstance(element, RequestF):
        path = urlparse(element.url).path.strip("/").split("/")
        env = []
        for i, path_part in enumerate(reversed(path)):
            env += [EnvE(f"request.path[{len(path)-i-1}]", Thunk(path_part))]
        return [EnvE(f"request.postData{e.name}", e.value) for e in element.postData] + env
    #if isinstance(element, ContentF):
    #    TODO: json
#    if isinstance(element, ResponseF):
#        return response.content
    if isinstance(element, EntryF):
        print(element.request + element.response)
        return element.request + element.response
    if isinstance(element, LogF):
        return element.entries
    if isinstance(element, TopF):
        return element.log
    return []


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
            url = element.url.split("?")[0]
            env = []
            queryString = []
            for q in element.queryString:
                env = q[1] + env
                queryString += [(q[0], list(env))]
#                print(env)
#                q[1] = list(env)
            env += [EnvE("Path", url)]
            return replace(element, url=url, headers=[], cookies=[], queryString=queryString), env
    if isinstance(element, ResponseF):
            return replace(element, headers=[], cookies=[]), []
#        case EntryF:
    if isinstance(element, EntryF):
            return element, element.request[1]
#        case LogF:
    if isinstance(element, LogF):
            env = element.entries[0][1]
            entries = [element.entries[0]]
            for e in element.entries:
                env = e[1] + env
                entries += [(e[0], list(env))]
            return replace(element, entries=entries), env
#        case TopF:
    if isinstance(element, TopF):
            return element, element.log[1]
    return element, []


#with open("test/www.demoblaze.com_Archive [22-05-30 13-47-04].har") as file:
with open("test/example1.har") as file:
    data = from_json(Har, file.read())

#pretty_print(cata(get_values, data))
from pprint import pprint
pprint(cata(build_env, data))

