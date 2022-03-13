from dataclasses import dataclass
from typing import Optional, List, Callable, Generic, TypeVar

from serde import serde

A = TypeVar("A")


@serde
class Creator(Generic[A]):
    name: str
    version: str
    comment: Optional[str]


CreatorAlg = Callable[[Creator[A]], A]

def creatorF(f: Callable[[str, str, Optional[str]], A], c: Creator) -> A:
    return f(c.name, c.version, c.comment)

@serde
class Cookie:
    name: str
    value: str
    path: Optional[str]
    domain: Optional[str]
    expires: Optional[str]
    httpOnly: Optional[bool]
    secure: Optional[bool]
    comment: Optional[str]

@serde
class Header:
    name: str
    value: str
    comment: Optional[str]

@serde
class QueryString:
    name: str
    value: str
    comment: Optional[str]

@serde
class Param:
    name: str
    value: Optional[str]
    fileName: Optional[str]
    contentType: Optional[str]
    comment: Optional[str]

@serde
class PostData:
    mimeType: str
    params: List[Param]
    text: str
    comment: Optional[str]

@serde
class Request:
    method: str
    url: str
    httpVersion: str
    cookies: List[Cookie]
    headers: List[Header]
    queryString: List[QueryString]
    headersSize: int
    bodySize: int
    postData: Optional[PostData]
    comment: Optional[str]

@serde
class Content:
    size: int
    mimeType: str
    compression: Optional[int]
    text: Optional[str]
    encoding: Optional[str]
    comment: Optional[str]

@serde
class Response:
    status: int
    statusText: str
    httpVersion: str
    cookies: List[Cookie]
    headers: List[Header]
    content: Content
    redirectURL: str
    headersSize: int
    bodySize: int
    comment: Optional[str]

@serde
class BeforeRequest:
    lastAccess: str
    eTag: str
    hitCount: int
    expires: Optional[str]
    comment: Optional[str]

@serde
class AfterRequest:
    lastAccess: str
    eTag: str
    hitCount: int
    expires: Optional[str]
    comment: Optional[str]

@serde
class Cache:
    beforeRequest: Optional[BeforeRequest]
    afterRequest: Optional[AfterRequest]
    comment: Optional[str]

@serde
class Timings:
    send: float
    wait: float
    receive: float
    blocked: Optional[float]
    dns: Optional[float]
    connect: Optional[float]
    ssl: Optional[float]
    comment: Optional[str]

@serde
class Entry:
    startedDateTime: str
    time: float
    request: Request
    response: Response
    cache: Cache
    timings: Timings
    pageref: Optional[str]
    serverIPAddress: Optional[str]
    connection: Optional[str]
    comment: Optional[str]

@serde
class Browser:
    name: str
    version: str
    comment: Optional[str]

@serde
class PageTimings:
    onContentLoad: Optional[int]
    onLoad: Optional[int]
    comment: Optional[str]

@serde
class Page:
    startedDateTime: str
    id: str
    title: str
    pageTimings: PageTimings
    comment: Optional[str]

@serde
class Log:
    creator: Creator
    entries: List[Entry]
    browser: Optional[Browser]
    pages: Optional[List[Page]]
    comment: Optional[str]
    version: str = "1.2"

@serde
class Har:
    log: Log


if __name__ == "__main__":
    from serde.json import from_json
    with open("./test/nix_search.har") as file:
        har = from_json(Har, file.read()).log
        print([e.request.url for e in har.entries])
