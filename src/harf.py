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


def cata(a: Callable[[HarF[A]], A], h: HarF) -> A:
    def inner_cata(e: HarF) -> A:
        return cata(a, e)

    return a(h.nmap(inner_cata, inner_cata))


QueryString = QueryStringF[Any, Any]
Cookie = CookieF[Any, Any]
Request = RequestF[QueryString, Cookie]
Entry = EntryF[Request, Any]

example = Entry(
    1,
    Request(
        "GET",
        "/api",
        [QueryString("q1", "v1"), QueryString("q2", "v2")],
        [Cookie("c", "c1")],
    ),
)


def fold(d: HarF[str]) -> str:
    if isinstance(d, QueryStringF):
        return f"{d.name}={d.value}"
    if isinstance(d, RequestF):
        return f"{d.method} {d.url}?{'&'.join(d.queryString)}"
    if isinstance(d, EntryF):
        return f"{d.request}\n"
    return ""


cata(fold, example)
