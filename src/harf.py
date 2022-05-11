from dataclasses import dataclass
from typing import TypeVar, Generic, Callable, List, Union, cast, Any

from serde import serde, SerdeSkip, field
from serde.json import from_json, to_json, JsonSerializer, JsonDeserializer

A = TypeVar("A")
B = TypeVar("B")
C = TypeVar("C")
D = TypeVar("D")


@serde
@dataclass
class QueryStringF(Generic[A, B]):
    name: str
    value: str

    def nmap(
        self: "QueryStringF[A, B]",
        f: Callable[[A], C],
        g: Callable[[B], D],
    ) -> "QueryStringF[C, D]":
        return cast(QueryStringF[C, D], self)

    def __str__(self):
        return f"QueryStringF(name={self.name}, value={self.value})"


@serde
@dataclass
class CookieF(Generic[A, B]):
    name: str
    value: str

    def nmap(
        self: "CookieF[A, B]",
        f: Callable[[A], C],
        g: Callable[[B], D],
    ) -> "CookieF[C, D]":
        return cast(CookieF[C, D], self)

    def __str__(self):
        return f"CookieF(name={self.name}, value={self.value})"


@serde
@dataclass
class RequestF(Generic[A, B]):
    method: str
    url: str
    queryString: List[A]
    cookies: List[B]

    def nmap(
        self: "RequestF[A, B]",
        f: Callable[[A], C],
        g: Callable[[B], D],
    ) -> "RequestF[C, D]":
        return RequestF(
            self.method,
            self.url,
            [f(q) for q in self.queryString],
            [g(c) for c in self.cookies],
        )

    def __str__(self):
        qs = ",".join(str(q) for q in self.queryString)
        cs = ",".join(str(c) for c in self.cookies)
        return f"RequestF(method={self.method}, url={self.url}, queryString=[{qs}], cookies=[{cs}])"


@serde
@dataclass
class EntryF(Generic[A, B]):
    time: float
    request: A

    def nmap(
        self: "EntryF[A, B]",
        f: Callable[[A], C],
        g: Callable[[B], D],
    ) -> "EntryF[C, D]":
        return EntryF(self.time, f(self.request))

    def __str__(self):
        return f"EntryF(time={self.time}, request={self.request})"


HarF = Union[QueryStringF[A, A], CookieF[A, A], RequestF[A, A], EntryF[A, A]]


@dataclass
class FixHar:
    unFix: HarF["FixHar"]

    def __str__(self) -> str:
        return str(self.unFix)


FixHar = serde(FixHar)



generated_to_dict = FixHar.__serde__.funcs['to_dict']

def to_dict(obj, *args, **kwargs):
    res = generated_to_dict(obj, *args, **kwargs)
    return res["unFix"]

generated_from_dict = FixHar.__serde__.funcs["from_dict"]

FixHar.__serde__.funcs["to_dict"] = to_dict


from serde.de import is_deserializable
from serde.compat import is_generic, get_origin, get_generic_arg

def from_dict(*args, cls, data, **kwargs):
#    print(cls.__serde__.union_se_args)
    def make_new_from_dict(type_):
        old_from_dict = type_.__serde__.funcs["from_dict"]
        def new_from_dict(*args, data, maybe_generic=None, **kwargs):
            print(type_)
            print(get_generic_arg(maybe_generic, 0))
            print(data)
            res= old_from_dict(*args, data=data, maybe_generic=maybe_generic, **kwargs)
            print(res)
            return res
        return new_from_dict
    for union in cls.__serde__.union_se_args.values():
        for type_ in union:
#            print(type_)
#            print(is_generic(type_))
            type_ = get_origin(type_)
#            print(type_)
#            print(is_deserializable(type_))
            type_.__serde__.funcs["from_dict"] = make_new_from_dict(type_)
#    print(data)
    data = {"unFix": data}
    res = generated_from_dict(*args, cls, data=data, **kwargs)
#    print(repr(res))
    return res


FixHar.__serde__.funcs["from_dict"] = from_dict

def query_string_f(name: str, value: str) -> FixHar:
    return FixHar(QueryStringF(name, value))


def cookie_f(name: str, value: str) -> FixHar:
    return FixHar(CookieF(name, value))


def request_f(
    method: str, url: str, query_string: List[FixHar], cookies: List[FixHar]
) -> FixHar:
    return FixHar(RequestF(method, url, query_string, cookies))


def entry_f(time: float, request: FixHar) -> FixHar:
    return FixHar(EntryF(time, request))


example = entry_f(
    1,
    request_f(
        "GET",
        "/api",
        [query_string_f("q1", "value1"), query_string_f("q2", "value2")],
        [cookie_f("c", "cookie")],
    ),
)
