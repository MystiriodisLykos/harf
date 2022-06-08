from serde.json import from_json

from collections.abc import Mapping, Iterable
from dataclasses import replace, is_dataclass, fields
from harf import cata, Har, QueryStringF, HeaderF, RequestF, ResponseF, EntryF, LogF, TopF, HarF
from typing import Any, NamedTuple, Tuple, List
from uuid import uuid4


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


pretty_print(cata(get_values, data))
