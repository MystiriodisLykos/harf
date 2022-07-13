from serde.json import from_json

from collections import defaultdict
from collections.abc import Mapping, Iterable
from dataclasses import replace, is_dataclass, fields, dataclass
from harf import cata, Har, QueryStringF, HeaderF, RequestF, ResponseF, EntryF, LogF, TopF, HarF, PostDataTextF, ContentF
from typing import Any, NamedTuple, Tuple, List, TypeVar, Generic, Callable, Union, NewType
from uuid import uuid4
from urllib.parse import urlparse
import json

A = TypeVar("A")
S = TypeVar("S")
R = TypeVar("R")


def json_fmap(source, f):
    if isinstance(source, list):
        return [f(e) for e in source]
    if isinstance(source, dict):
        return {k: f(v) for k, v in source.items()}
    return source

def json_cata(algebra: Callable[[A], R], source: S) -> R:
    def inner(element):
        return json_cata(algebra, element)
    return algebra(json_fmap(source, inner))


class Thunk(Generic[A]):
    _thunk_indices = []
    _thunk_values = []
    def __new__(cls, value: A):
        value=str(value)
        try:
            thunk_index = cls._thunk_indices.index(value)
            return cls._thunk_values[thunk_index]
        except ValueError:
            thunk = super().__new__(cls)
            cls._thunk_indices.append(value)
            cls._thunk_values.append(thunk)
            thunk._count = 0
            references = []
            return thunk
    def __init__(self, value: A):
        self._value = value
        self._count += 1
    def __eq__(self, other):
        return self._value == other._value
    def __repr__(self):
        return f"Thunk({self._value!r})|{id(self)}"
    def __hash__(self):
        return hash(self._value)

class EnvE(NamedTuple):
    name: str
    value: Thunk[Any]

Env = List[EnvE]


def json_env(json) -> Env:
    original = json_fmap(json, lambda e: e[1])
    thunk = Thunk(original)
    sub_envs = json_fmap(json, lambda e: e[0])
    if isinstance(json, list):
        ids = map(lambda e: f"[{e}]", range(len(sub_envs)))
    elif isinstance(json, dict):
        ids = map(lambda e: f".{e}", original.keys())
        sub_envs = sub_envs.values()
    else:
        return [EnvE("", thunk)], thunk
    env = []
    for id_, sub_env in zip(ids, sub_envs):
        sub_env = list(map(lambda e: EnvE(id_ + e.name, e.value), sub_env))
        env = sub_env + env
    return [EnvE("", thunk)] + env, thunk

def build_env(element: HarF[Env]) -> Env:
    if isinstance(element, PostDataTextF):
        return json_cata(json_env, json.loads(element.text))[0]
    if isinstance(element, RequestF):
        path = urlparse(element.url).path.strip("/").split("/")
        env = []
        for i, path_part in enumerate(reversed(path)):
            env += [EnvE(f"request.path[{len(path)-i-1}]", Thunk(path_part))]
        if element.postData != None:
            return [EnvE(f"request.postData{e.name}", e.value) for e in element.postData] + env
        return env
    if isinstance(element, ContentF):
        if element.text != "":
            return json_cata(json_env, json.loads(element.text))[0]
    if isinstance(element, ResponseF):
        return [EnvE(f"response.content{e.name}", e.value) for e in element.content]
    if isinstance(element, EntryF):
        return element.response + element.request
    if isinstance(element, LogF):
        env = []
        for i, sub_envs in enumerate(element.entries):
            env = [EnvE(f"{i+1}.{e.name}", e.value) for e in sub_envs] + env
        return env
    if isinstance(element, TopF):
        return element.log
    return []

def build_env2(element: HarF[Tuple[HarF, Env]]) -> Tuple[HarF, Env]:
#    if isinstance(element, PostDataF):
    if isinstance(element, RequestF):
        path = urlparse(element.url).path.strip("/").split("/")
        env = []
        new_path = []
        for i, path_part in enumerate(path):
            thunk = Thunk(path_part)
            name = f"request.path[{i}]"
            env = [EnvE(name, thunk)] + env
            new_path.append(name)
        return replace(element, url=new_path), env
    if isinstance(element, EntryF):
        request, request_env = element.request
        return replace(element, request=request), request_env
    if isinstance(element, LogF):
        env = []
        entries = []
        for entry in element.entries:
            entries.append(entry[0])
            env.extend(entry[1])
        return replace(element, entries=entries), env
    if isinstance(element, TopF):
        log, log_env = element.log
        return replace(element, log=log), log_env
    return element, []

IntId = NewType("IntId", int)
StrId = NewType("StrId", str)
PathId = NewType("PathId", IntId)

class RequestId(NamedTuple):
    path: PathId

class LogId(NamedTuple):
    entry: IntId
    request: RequestId

Id = List[Union[IntId, StrId, PathId, RequestId, LogId]]


def flatten(element: HarF[Env]) -> Env:
    if isinstance(element, TopF):
        return element.log
    if isinstance(element, LogF):
        env = []
        for i, entry in enumerate(element.entries):
            env.extend(map(lambda e: (LogId(i, e[0]), e[1]), entry))
        return env
    if isinstance(element, EntryF):
        return list(map(lambda e: (RequestId(e[0]), e[1]), element.request))
    if isinstance(element, RequestF):
        url = urlparse(element.url)
        path = url.path.strip("/").split("/")
        env = [(PathId(IntId(0)), f"{url.scheme}://{url.netloc}")]
        for i, path_part in enumerate(path):
            name = PathId(IntId(i+1))
            env.append((name, path_part))
        return env
    return []

def used_variables(env):
    usages = defaultdict(list)
    locations = defaultdict(list)
    for reference in env:
        if reference.value._count == 1:
            continue
        if "request" in reference.name:
            usages[reference.value].append(reference.name)
        elif reference.value in usages:
            locations[reference.value].append(reference.name)
    return {k: (usages[k], locations[k]) for k in usages}


#with open("test/www.demoblaze.com_Archive [22-05-30 13-47-04].har") as file:
with open("test/example1.har") as file:
    data = from_json(Har, file.read())

from pprint import pprint
pprint((cata(flatten, data)))

