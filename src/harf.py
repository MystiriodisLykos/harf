from dataclasses import dataclass
from functools import partial
from typing import TypeVar, Generic, Callable, List, Union, cast, Any, Optional

from serde import serde, SerdeSkip, field
from serde.json import from_json, to_json, JsonSerializer, JsonDeserializer

A = TypeVar("A")
B = TypeVar("B")
C = TypeVar("C")
D = TypeVar("D")

W = TypeVar("W")
X = TypeVar("X")
Y = TypeVar("Y")
Z = TypeVar("Z")

oint = Optional[int]
ostr = Optional[str]
obool = Optional[bool]
F = Callable[[A], B]


dint = partial(field, default=-1)


@serde
@dataclass
class TimingsF(Generic[A, B, C, D]):
    send: int
    wait: int
    receive: int
    blocked: oint = dint()
    dns: oint = dint()
    connect: oint = dint()
    ssl: oint = dint()
    comment: ostr = ""

    def nmap(
        self: "TimingsF[A, B, C, D]",
        f: F[A, W],
        g: F[B, X],
        h: F[C, Y],
        i: F[D, Z],
    ) -> "TimingsF[W, X, Y, Z]":
        return cast(TimingsF[W, X, Y, Z], self)


@serde
@dataclass
class BeforeAfterRequestF(Generic[A, B, C, D]):
    lastAccess: str
    eTag: str
    hitCount: int
    expires: ostr = None
    commint: ostr = ""

    def nmap(
        self: "BeforeAfterRequestF[A, B, C, D]",
        f: F[A, W],
        g: F[B, X],
        h: F[C, Y],
        i: F[D, Z],
    ) -> "BeforeAfterRequestF[W, X, Y, Z]":
        return cast(BeforeAfterRequestF[W, X, Y, Z], self)


@serde
@dataclass
class CacheF(Generic[A, B, C, D]):
    beforeRequest: A
    afterRequest: B

    def namp(
        self: "CacheF[A, B, C, D]",
        f: F[A, W],
        g: F[B, X],
        h: F[C, Y],
        i: F[D, Z],
    ) -> "CacheF[W, X, Y, Z]":
        return CacheF(f(self.beforeRequest), g(self.afterRequest))


@serde
@dataclass
class ContentF(Generic[A, B, C, D]):
    size: int
    mimeType: str
    compression: oint = None
    text: ostr = ""
    encoding: ostr = ""
    comment: ostr = ""

    def nmap(
        self: "ContentF[A, B, C, D]",
        f: F[A, W],
        g: F[B, X],
        h: F[C, Y],
        i: F[D, Z],
    ) -> "ContentF[W, X, Y, Z]":
        return cast(ContentF[W, X, Y, Z], self)


@serde
@dataclass
class HeaderF(Generic[A, B]):
    name: str
    value: str
    comment: ostr = ""

    def nmap(self: "HeaderF[A, B]", f: F[A, C], g: F[B, D]) -> "HeaderF[C, D]":
        return cast(HeaderF[C, D], self)


@serde
@dataclass
class CookieF(Generic[A, B]):
    name: str
    value: str
    path: ostr = None
    domain: ostr = None
    expired: ostr = None
    httpOnly: obool = None
    secure: obool = None
    comment: ostr = ""

    def nmap(
        self: "CookieF[A, B]",
        f: Callable[[A], C],
        g: Callable[[B], D],
    ) -> "CookieF[C, D]":
        return cast(CookieF[C, D], self)


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
