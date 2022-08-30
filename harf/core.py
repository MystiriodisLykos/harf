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
class TimingsF:
    send: int
    wait: int
    receive: int
    blocked: oint = dint()
    dns: oint = dint()
    connect: oint = dint()
    ssl: oint = dint()
    comment: ostr = ""

    def nmap(self: "TimingsF") -> "TimingsF":
        return self


@serde
@dataclass
class BeforeAfterRequestF:
    lastAccess: str
    eTag: str
    hitCount: int
    expires: ostr = None
    comment: ostr = ""

    def nmap(self: "BeforeAfterRequestF") -> "BeforeAfterRequestF":
        return self


@serde
@dataclass
class CacheF(Generic[A, B]):
    beforeRequest: Optional[A] = None
    afterRequest: Optional[B] = None
    comment: ostr = ""

    def nmap(self: "CacheF[A, B]", f: F[A, W], g: F[B, X]) -> "CacheF[W, X]":
        return CacheF(
            f(self.beforeRequest) if self.beforeRequest else None,
            g(self.afterRequest) if self.afterRequest else None,
        )


@serde
@dataclass
class ContentF:
    size: int
    mimeType: str
    compression: oint = None
    text: ostr = ""
    encoding: ostr = ""
    comment: ostr = ""

    def nmap(self: "ContentF") -> "ContentF":
        return self


@serde
@dataclass
class ResponseF(Generic[A, B, C]):
    status: int
    statusText: str
    httpVersion: str
    cookies: List[A]
    headers: List[B]
    content: C
    redirectURL: str
    headersSize: int = -1
    bodySize: int = -1
    comment: ostr = ""

    def nmap(
        self: "ResponseF[A, B, C]",
        f: F[A, W],
        g: F[B, X],
        h: F[C, Y],
    ) -> "ResponseF[W, X, Y]":
        return replace(
            self,  # type: ignore[arg-type]
            cookies=list(map(f, self.cookies)),
            headers=list(map(g, self.headers)),
            content=h(self.content),
        )


@serde
@dataclass
class ParamF:
    name: str
    value: ostr = None
    fileName: ostr = None
    contentType: ostr = None
    comment: ostr = ""

    def nmap(self: "ParamF") -> "ParamF":
        return self


@serde
@dataclass
class PostDataParamF(Generic[A]):
    mimeType: str
    params: List[A]
    comment: ostr = ""

    def nmap(self: "PostDataParamF[A]", f: F[A, W]) -> "PostDataParamF[W]":
        return replace(
            self,  # type: ignore[arg-type]
            params=list(map(f, self.params)),
        )


@serde
@dataclass
class PostDataTextF:
    mimeType: str
    text: str
    comment: ostr = ""

    def nmap(self: "PostDataTextF") -> "PostDataTextF":
        return self


PostDataF = Union[PostDataTextF, PostDataParamF[A]]


@serde
@dataclass
class QueryStringF:
    name: str
    value: str
    comment: ostr = ""

    def nmap(self: "QueryStringF") -> "QueryStringF":
        return self


@serde
@dataclass
class HeaderF:
    name: str
    value: str
    comment: ostr = ""

    def nmap(self: "HeaderF") -> "HeaderF":
        return self


@serde
@dataclass
class CookieF:
    name: str
    value: str
    path: ostr = None
    domain: ostr = None
    expired: ostr = None
    httpOnly: obool = None
    secure: obool = None
    comment: ostr = ""

    def nmap(self: "CookieF") -> "CookieF":
        return self


@serde
@dataclass
class RequestF(Generic[A, B, C, D]):
    method: str
    url: str
    httpVersion: str
    cookies: List[A]
    headers: List[B]
    queryString: List[C]
    headersSize: int
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
        post_data = self.postData
        if post_data is not None:
            new_post_data: Optional[Z] = i(post_data)
        else:
            new_post_data = post_data
        return replace(
            self,  # type: ignore[arg-type]
            cookies=list(map(f, self.cookies)),
            headers=list(map(g, self.headers)),
            queryString=list(map(h, self.queryString)),
            postData=new_post_data,
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
class PageTimingsF:
    onContentLoad: oint = -1
    onLoad: oint = -1
    comment: ostr = ""

    def nmap(self: "PageTimingsF") -> "PageTimingsF":
        return self


@serde
@dataclass
class PageF(Generic[A]):
    startedDateTime: str
    id: str
    title: str
    pageTimings: A
    comment: ostr = ""

    def nmap(self: "PageF[A]", f: F[A, W]) -> "PageF[W]":
        return replace(
            self,  # type: ignore[arg-type]
            pageTimings=f(self.pageTimings),
        )


@serde
@dataclass
class BrowserF:
    name: str
    version: str
    comment: ostr = ""

    def nmap(self: "BrowserF") -> "BrowserF":
        return self


@serde
@dataclass
class CreatorF:
    name: str
    version: str
    comment: ostr = ""

    def nmap(self: "CreatorF") -> "CreatorF":
        return self


@serde
@dataclass
class LogF(Generic[A, B, C, D]):
    creator: A
    entries: List[B]
    pages: List[D] = field(default_factory=list)
    version: str = "1.2"
    browser: Optional[C] = None
    comment: ostr = ""

    def nmap(
        self: "LogF[A, B, C, D]",
        f: F[A, W],
        g: F[B, X],
        h: F[C, Y],
        i: F[D, Z],
    ) -> "LogF[W, X, Y, Z]":
        browser = self.browser
        if browser is None:
            new_browser: Optional[Y] = browser
        else:
            new_browser = h(browser)
        return replace(
            self,  # type: ignore[arg-type]
            creator=f(self.creator),
            entries=list(map(g, self.entries)),
            browser=new_browser,
            pages=list(map(i, self.pages)),
        )


@serde
@dataclass
class TopF(Generic[A]):
    log: A

    def nmap(self: "TopF[A]", f: F[A, W]) -> "TopF[W]":
        return TopF(f(self.log))


HarF = Union[
    TimingsF,
    BeforeAfterRequestF,
    CacheF[A, A],
    ContentF,
    ResponseF[A, A, A],
    ParamF,
    PostDataF[A],
    QueryStringF,
    HeaderF,
    CookieF,
    RequestF[A, A, A, A],
    EntryF[A, A, A, A],
    PageTimingsF,
    PageF[A],
    BrowserF,
    CreatorF,
    LogF[A, A, A, A],
    TopF,
]


FHar = HarF["FHar"]  # type: ignore[misc]


def cata(a: Callable[[HarF[A]], A], h: FHar) -> A:
    def inner_cata(e: HarF) -> A:
        return cata(a, e)

    fs = [inner_cata] * len(getattr(h, "__parameters__", []))
    return a(h.nmap(*fs))


def harf(
    timing: Callable[[TimingsF], A] = None,
    before_after_request: Callable[[BeforeAfterRequestF], A] = None,
    cache: Callable[[CacheF], A] = None,
    content: Callable[[ContentF], A] = None,
    response: Callable[[ResponseF[A, A, A]], A] = None,
    param: Callable[[ParamF], A] = None,
    post_data: Callable[[PostDataF[A]], A] = None,
    querystring: Callable[[QueryStringF], A] = None,
    header: Callable[[HeaderF], A] = None,
    cookie: Callable[[CookieF], A] = None,
    request: Callable[[RequestF[A, A, A, A]], A] = None,
    entry: Callable[[EntryF[A, A, A, A]], A] = None,
    page_timing: Callable[[PageTimingsF], A] = None,
    page: Callable[[PageF[A]], A] = None,
    browser: Callable[[BrowserF], A] = None,
    creator: Callable[[CreatorF], A] = None,
    log: Callable[[LogF[A, A, A, A]], A] = None,
    default: A = None,
) -> Callable[[FHar], A]:
    def alg(h: HarF[A]) -> A:
        if isinstance(h, TimingsF):
            return timing(h) if timing else default
        if isinstance(h, BeforeAfterRequestF):
            return before_after_request(h) if before_after_request else default
        if isinstance(h, CacheF):
            return cache(h) if cache else default
        if isinstance(h, ContentF):
            return content(h) if content else default
        if isinstance(h, ResponseF):
            return response(h) if response else default
        if isinstance(h, ParamF):
            return param(h) if param else default
        if isinstance(h, PostDataTextF) or isinstance(h, PostDataParamF):
            return post_data(h) if post_data else default
        if isinstance(h, QueryStringF):
            return querystring(h) if querystring else default
        if isinstance(h, HeaderF):
            return header(h) if header else default
        if isinstance(h, CookieF):
            return cookie(h) if cookie else default
        if isinstance(h, RequestF):
            return request(h) if request else default
        if isinstance(h, EntryF):
            return entry(h) if entry else default
        if isinstance(h, PageTimingsF):
            return page_timing(h) if page_timing else default
        if isinstance(h, PageF):
            return page(h) if page else default
        if isinstance(h, BrowserF):
            return browser(h) if browser else default
        if isinstance(h, CreatorF):
            return creator(h) if creator else default
        if isinstance(h, LogF):
            return log(h) if log else default
        if isinstance(h, TopF):
            return h.log
        return default

    return partial(cata, alg)


Timings = TimingsF
BeforeAfterRequest = BeforeAfterRequestF
Cache = CacheF[BeforeAfterRequest, BeforeAfterRequest]
Content = ContentF
Header = HeaderF
Cookie = CookieF
Response = ResponseF[Cookie, Header, Content]
Param = ParamF
PostData = PostDataF[Param]
QueryString = QueryStringF
Request = RequestF[Cookie, Header, QueryString, PostData]
Entry = EntryF[Request, Response, Cache, Timings]
PageTimings = PageTimingsF
Page = PageF[PageTimings]
Browser = BrowserF
Creator = CreatorF
Log = LogF[Creator, Entry, Browser, Page]
Har = TopF[Log]

"""
example = Entry(
    "dafsd",
    1,
    Request(
        "GET",
        "/api",
        "1.1",
        [Cookie("c", "c1")],
        [],
        [QueryString("q1", "v1"), QueryString("q2", "v2")],
        0,
        0,
    ),
    Response(
        200,
        "OK",
        "1.1",
        [],
        [],
        ContentF(0, ""),
        "",
    ),
    Cache(None, None),
    Timings(1, 1, 1),
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
