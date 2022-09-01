from enum import Enum
from typing import get_args
from string import printable

from hypothesis import strategies as st

from harf.core import TimingsF, BeforeAfterRequestF, CacheF, ContentF, Cache

text = st.text(printable)
comment = text | st.none()
positive_int = st.integers(0)
optional_int = positive_int | st.just(-1) | st.none()
datetime = st.datetimes().map(lambda d: d.strftime("%Y-%m-%dT%H:%M:%S"))


class MimeTypes(Enum):
    TEXT_PLAIN = 0


@st.composite
def timings(draw):
    print("timings")
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


st.register_type_strategy(TimingsF, timings)

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
    print("cache")
    try:
        before, after = get_args(t)
        print(before, after)
    except ValueError as e:
        raise ValueError(f"Cannot create generic type {t}") from e
    return st.builds(
        CacheF,
        beforeRequest=st.from_type(before) | st.none(),
        afterRequest=st.from_type(after) | st.none(),
        comment=comment,
    )


st.register_type_strategy(CacheF, cache)

"""
@st.composite
def content(draw):
    print("content")
    mimeType = draw(st.sampled_from(MimeTypes))
    if mimeType == MimeTypes.TEXT_PLAIN:
        text_ = draw(text)
    return ContentF(
        size=len(text_),
        mimeType=mimeType,
        text=text_,
        comment=draw(comment),
    )

st.register_type_strategy(ContentF, content)
"""
print("lkandlfk")
print(cache(Cache).example())
print(st.builds(Cache).example())
