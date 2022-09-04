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


class MimeTypes(Enum):
    TEXT_PLAIN = 0
    JSON = 1


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
def content(draw):
    mimeType = draw(st.sampled_from(MimeTypes))
    if mimeType == MimeTypes.TEXT_PLAIN:
        text_ = draw(text)
    elif mimeType == MimeTypes.JSON:
        text_ = str(draw(json))
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


@given(timing=infer)
def test_timings_ssl_in_connect(timing: TimingsF):
    """Tests that generated timings that include `ssh` include the time in `connect`"""
    assume(timing.ssl is not None)
    assert timing.connect >= timing.ssl


@given(response=infer)
def test_response_uses_registered_content_strategy(response: Response):
    """Tests that generating a Response instance uses the registered strategy for the internal Content"""
    assert response.conent.size >= 0
