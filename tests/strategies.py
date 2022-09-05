from enum import Enum
from typing import get_args
from string import printable

from hypothesis import assume, given, infer, strategies as st

from harf.core import (
    TimingsF,
    BeforeAfterRequestF,
    CacheF,
    ContentF,
    HeaderF,
    CookieF,
    ResponseF,
    Response,
    ParamF
)

text = st.text(printable)
comment = text | st.none()
positive_int = st.integers(0)
optional_int = positive_int | st.just(-1) | st.none()
datetime = st.datetimes().map(lambda d: d.strftime("%Y-%m-%dT%H:%M:%S"))

json = st.recursive(
    st.none() | st.booleans() | st.floats() | text | st.integers(),
    lambda children: st.lists(children) | st.dictionaries(text, children),
)


class MimeTypes(str, Enum):
    TEXT_PLAIN = "text"
    JSON = "application/json"

@st.composite
def mime_data(draw):
    mime_type = draw(st.sampled_from(MimeTypes)).value
    if mime_type == MimeTypes.TEXT_PLAIN:
        return mime_type, draw(text)
    elif mime_type == MimeTypes.JSON:
        return mime_type, str(draw(json))

@st.composite
def timings(draw):
    ssl = draw(optional_int)
    connect = draw(st.integers(ssl) if ssl is not None else optional_int)
    return TimingsF(
        send=draw(positive_int),
        wait=draw(positive_int),
        receive=draw(positive_int),
        ssl=ssl,
        connect=connect,
        blocked=draw(optional_int),
        dns=draw(optional_int),
        comment=draw(comment),
    )


st.register_type_strategy(TimingsF, timings())


before_after_request = st.builds(
    BeforeAfterRequestF,
    eTag=text,
    lastAccess=datetime,
    hitCount=positive_int,
    expires=datetime | st.none(),
    comment=comment,
)

st.register_type_strategy(BeforeAfterRequestF, before_after_request)


def cache(t):
    try:
        before, after = get_args(t)
    except ValueError as e:
        raise ValueError(f"Cannot create generic type {t}") from e
    return st.builds(
        CacheF,
        beforeRequest=st.from_type(before) | st.none(),
        afterRequest=st.from_type(after) | st.none(),
        comment=comment,
    )


st.register_type_strategy(CacheF, cache)


@st.composite
def content(draw):  # todo: change this to take a strategy for building mime data
    mimeType, text_ = draw(mime_data())
    return ContentF(
        size=len(text_),
        mimeType=mimeType,
        text=text_,
        comment=draw(comment),
    )


st.register_type_strategy(ContentF, content())


header = st.builds(
    HeaderF,
    name=text,
    value=text,
    comment=comment,
)

st.register_type_strategy(HeaderF, header)


cookie = st.builds(
    CookieF,
    name=text,
    value=text,
    path=comment,
    domain=comment,
    expires=datetime | st.none(),
    httpOnly=st.booleans(),
    secure=st.booleans(),
    comment=comment,
)

st.register_type_strategy(CookieF, cookie)


def response(t):
    try:
        cookie, header, content = get_args(t)
    except ValueError as e:
        raise ValueError(f"Cannot create generic type {t}") from e
    return st.builds(
        ResponseF,
        status=positive_int,
        statusText=text,
        httpVersion=st.just("HTTP/1.1"),
        cookies=st.lists(st.from_type(cookie)),
        headers=st.lists(st.from_type(header)),
        content=st.from_type(content),
        redirectURL=text,
        headersSize=positive_int,
        bodySize=positive_int,
        comment=comment,
    )


st.register_type_strategy(ResponseF, response)

@st.composite
def param(draw):  # todo: change this to take a strategy for building mime data
    include_file = draw(st.booleans())
    contentType = None
    fileName = st.none()
    value = draw(comment)
    if include_file:
        contentType, value  = draw(mime_data())
        fileName = text
    return ParamF(
        name=draw(text),
        value=value,
        fileName=draw(fileName),
        contentType=contentType,
        comment=draw(comment),
    )

st.register_type_strategy(ParamF, param())

def post_data_param(t):
    try:
        param = get_args(t)
    except ValueError as e:
        raise ValueError(f"Cannot create generic type {t}") from e
    raise st.builds(
        PostDataParamF,
        mimeType=st.sampled_from(MimeTypes),
        params=st.lists(st.from_type(param)),
        comment=comment,
    )

@st.composite
def post_data_text(draw):
    mimeType, text = draw(mime_data())
    return PostDataTextF(
        mimeType=mimeType,
        text=text,
        comment=draw(comment),
    )

queryString = st.builds(
    QueryStringF,
    name=text,
    value=text,
    comment=comment
)


@given(timing=infer)
def test_timings_ssl_in_connect(timing: TimingsF):
    """Tests that generated timings that include `ssh` include the time in `connect`"""
    assume(timing.ssl is not None)
    assert timing.connect >= timing.ssl

@given(cache=infer)
def test_cache_uses_provided_types(cache: CacheF[int, str]):
    """Tests CacheF instances are built with provided type params"""
    assert isinstance(cache.before, int)
    assert isinstance(cache.after, str)

@given(response=infer)
def test_response_uses_provided_header_type(response: ResponseF[None, int, None]):
    assume(len(response.headers))
    for h in response.headers:
        assert isinstance(h, int)

@given(response=infer)
def test_response_uses_provided_cookie_type(response: ResponseF[int, None, None]):
    assume(len(response.cookies))
    for c in response.cookies:
        assert isinstance(c, int)

@given(response=infer)
def test_response_uses_provided_content_type(response: ResponseF[int, int, ContentF]):
    assert isinstance(response.content, ContentF)
    assert response.content.size >= 0
