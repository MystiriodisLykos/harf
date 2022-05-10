from dataclasses import dataclass
from typing import TypeVar, Generic, Callable, List, Union, cast

from serde import serde, SerdeSkip
from serde.json import from_json, to_json

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


def seralize(cls, o):
    print(cls)
    print()
    print(o)
    print()
    print()
    raise SerdeSkip()


@dataclass
class FixHar:
    unFix: HarF["FixHar"]

    def __str__(self) -> str:
        return str(self.unFix)

FixHar = serde(FixHar, serializer=seralize, deserializer=seralize)

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
