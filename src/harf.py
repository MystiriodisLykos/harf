from dataclasses import dataclass, replace
from functools import partial
from typing import TypeVar, Generic, Callable, List, Union, Any, Optional

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
        return self  # type: ignore[return-value]


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
        return self  # type: ignore[return-value]


@serde
@dataclass
class CacheF(Generic[A, B, C, D]):
    beforeRequest: A
    afterRequest: B

    def nmap(
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
        return self  # type: ignore[return-value]


@serde
@dataclass
class ResponseF(Generic[A, B, C, D]):
    status: int
    statusText: str
    httpVersion: str
    cookies: List[A]
    headers: List[B]
    content: C
    redirectURL: str
    headerSize: int = -1
    bodySize: int = -1
    comment: ostr = ""

    def nmap(
        self: "ResponseF[A, B, C, D]",
        f: F[A, W],
        g: F[B, X],
        h: F[C, Y],
        i: F[D, Z],
    ) -> "ResponseF[W, X, Y, Z]":
        return replace(
            self,  # type: ignore[arg-type]
            cookies=list(map(f, self.cookies)),
            headers=list(map(g, self.headers)),
            content=h(self.content),
        )


@serde
@dataclass
class ParamF(Generic[A, B, C, D]):
    name: str
    value: ostr = None
    fileName: ostr = None
    contentType: ostr = None
    comment: ostr = ""

    def nmap(
        self: "ParamF[A, B, C, D]",
        f: F[A, W],
        g: F[B, X],
        h: F[C, Y],
        i: F[D, Z],
    ) -> "ParamF[W, X, Y, Z]":
        return self  # type: ignore[return-value]


@serde
@dataclass
class PostDataParamF(Generic[A, B, C, D]):
    mimeType: str
    params: List[A]
    comment: ostr = ""

    def nmap(
        self: "PostDataParamF[A, B, C, D]",
        f: F[A, W],
        g: F[B, X],
        h: F[C, Y],
        i: F[D, Z],
    ) -> "PostDataParamF[W, X, Y, Z]":
        return replace(
            self,  # type: ignore[arg-type]
            params=list(map(f, self.params)),
        )


@serde
@dataclass
class PostDataTextF(Generic[A, B, C, D]):
    mimeType: str
    text: str
    comment: ostr = ""

    def nmap(
        self: "PostDataTextF[A, B, C, D]",
        f: F[A, W],
        g: F[B, X],
        h: F[C, Y],
        i: F[D, Z],
    ) -> "PostDataTextF[W, X, Y, Z]":
        return self  # type: ignore[return-value]


PostDataF = Union[PostDataParamF[A, B, C, D], PostDataTextF[A, B, C, D]]


@serde
@dataclass
class QueryStringF(Generic[A, B, C, D]):
    name: str
    value: str
    comment: ostr = ""

    def nmap(
        self: "QueryStringF[A, B, C, D]",
        f: F[A, W],
        g: F[B, X],
        h: F[C, Y],
        i: F[D, Z],
    ) -> "QueryStringF[W, X, Y, Z]":
        return self  # type: ignore[return-value]


@serde
@dataclass
class HeaderF(Generic[A, B, C, D]):
    name: str
    value: str
    comment: ostr = ""

    def nmap(
        self: "HeaderF[A, B, C, D]",
        f: F[A, W],
        g: F[B, X],
        h: F[C, Y],
        i: F[D, Z],
    ) -> "HeaderF[W, X, Y, Z]":
        return self  # type: ignore[return-value]


@serde
@dataclass
class CookieF(Generic[A, B, C, D]):
    name: str
    value: str
    path: ostr = None
    domain: ostr = None
    expired: ostr = None
    httpOnly: obool = None
    secure: obool = None
    comment: ostr = ""

    def nmap(
        self: "CookieF[A, B, C, D]",
        f: F[A, W],
        g: F[B, X],
        h: F[C, Y],
        i: F[D, Z],
    ) -> "CookieF[W, X, Y, Z]":
        return self  # type: ignore[return-value]


@serde
@dataclass
class RequestF(Generic[A, B, C, D]):
    method: str
    url: str
    httpVersion: str
    cookies: List[A]
    headers: List[B]
    queryString: List[C]
    headerSize: int
    bodySize: int
    postData: Optional[D] = None
    comment: ostr = ""

    def nmap(
        self: "RequestF[A, B, C, D]",
        f: F[A, W],
        g: F[B, X],
        h: F[C, Y],
        i: F[D, Z],
    ) -> "RequestF[W, X, Y, Z]":
        return replace(
            self,  # type: ignore[arg-type]
            cookies=list(map(f, self.cookies)),
            headers=list(map(g, self.headers)),
            queryString=list(map(h, self.queryString)),
            postData=i(self.postData) if self.postData != None else None,
        )


@serde
@dataclass
class EntryF(Generic[A, B, C, D]):
    startedDateTime: str
    time: int
    request: A
    response: B
    cache: C
    timings: D
    serverIPAddress: ostr = None
    connection: ostr = None
    comment: ostr = ""

    def nmap(
        self: "EntryF[A, B, C, D]",
        f: F[A, W],
        g: F[B, X],
        h: F[C, Y],
        i: F[D, Z],
    ) -> "EntryF[W, X, Y, Z]":
        return replace(
            self,  # type: ignore[arg-type]
            request=f(self.request),
            response=g(self.response),
            cache=h(self.cache),
            timings=i(self.timings),
        )


@serde
@dataclass
class PageTimingsF(Generic[A, B, C, D]):
    onContentLoad: oint = -1
    onLoad: oint = -1
    comment: ostr = ""

    def nmap(
        self: "PageTimingsF[A, B, C, D]",
        f: F[A, W],
        g: F[B, X],
        h: F[C, Y],
        i: F[D, Z],
    ) -> "PageTimingsF[W, X, Y, Z]":
        return self  # type: ignore[return-value]


@serde
@dataclass
class PageF(Generic[A, B, C, D]):
    startedDateTime: str
    id: str
    title: str
    pageTimings: A
    comment: ostr = ""

    def nmap(
        self: "PageF[A, B, C, D]",
        f: F[A, W],
        g: F[B, X],
        h: F[C, Y],
        i: F[D, Z],
    ) -> "PageF[W, X, Y, Z]":
        return replace(
            self,  # type: ignore[arg-type]
            pageTimings=f(self.pageTimings),
        )


@serde
@dataclass
class BrowserF(Generic[A, B, C, D]):
    name: str
    version: str
    comment: ostr = ""

    def nmap(
        self: "BrowserF[A, B, C, D]",
        f: F[A, W],
        g: F[B, X],
        h: F[C, Y],
        i: F[D, Z],
    ) -> "BrowserF[W, X, Y, Z]":
        return self  # type: ignore[return-value]


@serde
@dataclass
class CreatorF(Generic[A, B, C, D]):
    name: str
    version: str
    comment: ostr = ""

    def nmap(
        self: "CreatorF[A, B, C, D]",
        f: F[A, W],
        g: F[B, X],
        h: F[C, Y],
        i: F[D, Z],
    ) -> "CreatorF[W, X, Y, Z]":
        return self  # type: ignore[return-value]


@serde
@dataclass
class LogF(Generic[A, B, C, D]):
    creator: A
    entries: List[B]
    version: str = "1.2"
    browser: Optional[C] = None
    pages: List[D] = field(default_factor=list)
    comment: ostr = ""

    def nmap(
        self: "LogF[A, B, C, D]",
        f: F[A, W],
        g: F[B, X],
        h: F[C, Y],
        i: F[D, Z],
    ) -> "LogF[W, X, Y, Z]":
        return replace(
            self,  # type: ignore[arg-type]
            creator=f(self.creator),
            entries=list(map(g, self.entries)),
            browser=h(self.browser) if self.browser != None else None,
            pages=list(map(i, self.pages)),
        )


HarF = Union[
    TimingsF[A, A, A, A],
    BeforeAfterRequestF[A, A, A, A],
    CacheF[A, A, A, A],
    ContentF[A, A, A, A],
    ResponseF[A, A, A, A],
    ParamF[A, A, A, A],
    PostDataF[A, A, A, A],
    QueryStringF[A, A, A, A],
    HeaderF[A, A, A, A],
    CookieF[A, A, A, A],
    RequestF[A, A, A, A],
    EntryF[A, A, A, A],
    PageTimingsF[A, A, A, A],
    PageF[A, A, A, A],
    BrowserF[A, A, A, A],
    CreatorF[A, A, A, A],
    LogF[A, A, A, A],
]


def cata(a: Callable[[HarF[A]], A], h: HarF) -> A:
    def inner_cata(e: HarF) -> A:
        return cata(a, e)

    return a(h.nmap(inner_cata, inner_cata, inner_cata, inner_cata))


Timings = TimingsF[Any, Any, Any, Any]
BeforeAfterRequest = BeforeAfterRequestF[Any, Any, Any, Any]
Cache = CacheF[BeforeAfterRequest, BeforeAfterRequest, Any, Any]
Content = ContentF[Any, Any, Any, Any]
Header = HeaderF[Any, Any, Any, Any]
Cookie = CookieF[Any, Any, Any, Any]
Response = ResponseF[Cookie, Header, Content, Any]
Param = ParamF[Any, Any, Any, Any]
PostData = PostDataF[Param, Any, Any, Any]
QueryString = QueryStringF[Any, Any, Any, Any]
Request = RequestF[Cookie, Header, QueryString, PostData]
Entry = EntryF[Request, Response, Cache, Timings]
PageTimings = PageTimingsF[Any, Any, Any, Any]
Page = PageF[PageTimings, Any, Any, Any]
Browser = BrowserF[Any, Any, Any, Any]
Creator = CreatorF[Any, Any, Any, Any]
Log = LogF[Creator, Entry, Browser, Page]

"""
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
"""
