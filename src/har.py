from dataclasses import dataclass
from typing import Optional, List

from serde import serialize, deserialize

@serialize
@deserialize
@dataclass
class Creator:
    name: str
    version: str
    comment: Optional[str] = None


@serialize
@deserialize
@dataclass
class Cookie:
    name: str
    value: str
    path: Optional[str] = None
    domain: Optional[str] = None
    expires: Optional[str] = None
    httpOnly: Optional[bool] = None
    secure: Optional[bool] = None
    comment: Optional[str] = None

@serialize
@deserialize
@dataclass
class Header:
    name: str
    value: str
    comment: Optional[str] = None

@serialize
@deserialize
@dataclass
class QueryString:
    name: str
    value: str
    comment: Optional[str] = None

@serialize
@deserialize
@dataclass
class Param:
    name: str
    value: Optional[str] = None
    fileName: Optional[str] = None
    contentType: Optional[str] = None
    comment: Optional[str] = None

@serialize
@deserialize
@dataclass
class PostData:
    mimeType: str
    params: List[Param]
    text: str
    comment: Optional[str] = None

@serialize
@deserialize
@dataclass
class Request:
    method: str
    url: str
    httpVersion: str
    cookies: List[Cookie]
    headers: List[Header]
    queryString: List[QueryString]
    headersSize: int
    bodySize: int
    postData: Optional[PostData] = None
    comment: Optional[str] = None

@serialize
@deserialize
@dataclass
class Content:
    size: int
    mimeType: str
    compression: Optional[int] = None
    text: Optional[str] = None
    encoding: Optional[str] = None
    comment: Optional[str] = None

@serialize
@deserialize
@dataclass
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
    comment: Optional[str] = None

@serialize
@deserialize
@dataclass
class BeforeRequest:
    lastAccess: str
    eTag: str
    hitCount: int
    expires: Optional[str] = None
    comment: Optional[str] = None

@serialize
@deserialize
@dataclass
class AfterRequest:
    lastAccess: str
    eTag: str
    hitCount: int
    expires: Optional[str] = None
    comment: Optional[str] = None

@serialize
@deserialize
@dataclass
class Cache:
    beforeRequest: Optional[BeforeRequest] = None
    afterRequest: Optional[AfterRequest] = None
    comment: Optional[str] = None

@serialize
@deserialize
@dataclass
class Timings:
    send: float
    wait: float
    receive: float
    blocked: Optional[float] = None
    dns: Optional[float] = None
    connect: Optional[float] = None
    ssl: Optional[float] = None
    comment: Optional[str] = None

@serialize
@deserialize
@dataclass
class Entry:
    startedDateTime: str
    time: float
    request: Request
    response: Response
    cache: Cache
    timings: Timings
    pageref: Optional[str] = None
    serverIPAddress: Optional[str] = None
    connection: Optional[str] = None
    comment: Optional[str] = None

@serialize
@deserialize
@dataclass
class Browser:
    name: str
    version: str
    comment: Optional[str] = None

@serialize
@deserialize
@dataclass
class PageTimings:
    onContentLoad: Optional[int] = None
    onLoad: Optional[int] = None
    comment: Optional[str] = None

@serialize
@deserialize
@dataclass
class Page:
    startedDateTime: str
    id: str
    title: str
    pageTimings: PageTimings
    comment: Optional[str] = None

@serialize
@deserialize
@dataclass
class Log:
    creator: Creator
    entries: List[Entry]
    version: str = "1.2"
    browser: Optional[Browser] = None
    pages: Optional[List[Page]] = None
    comment: Optional[str] = None


@serialize
@deserialize
@dataclass
class Har:
    log: Log


if __name__ == "__main__":
    from serde.json import from_json
    with open("./test/nix_search.har") as file:
        har = from_json(Har, file.read()).log
        print([e.request.url for e in har.entries])
