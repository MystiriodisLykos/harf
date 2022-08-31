from typing import get_args
from string import printable

from hypothesis import strategies as st

from harf.core import TimingsF, BeforeAfterRequestF, CacheF, Content, Cache

text = st.text(printable)
comment = text | st.none()
positive_int = st.integers(0)
optional_int = positive_int | st.just(-1) | st.none()
datetime = st.datetimes().map(lambda d: d.strftime("%Y-%m-%dT%H:%M:%S"))

timings = st.builds(
    TimingsF,
    send=positive_int,
    wait=positive_int,
    receive=positive_int,
    ssl=optional_int,
    connect=optional_int,
    blocked=optional_int,
    dns=optional_int,
    comment=comment,
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
    try:
        before, after = get_args(t)
    except ValueError as e:
        raise ValueError (f"Cannot create generic type {t}") from e
    print(before, after)
    return st.builds(
        CacheF,
        beforeRequest=st.from_type(before) | st.none(),
        afterRequest=st.from_type(after) | st.none(),
        comment=comment,
    )

st.register_type_strategy(CacheF, cache)

def content(t):
    
