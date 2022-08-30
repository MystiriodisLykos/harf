from string import printable
from hypothesis import strategies as st

from harf.core import TimingsF, BeforeAfterRequestF, CacheF, ContentF

text = st.text(printable)
positive_int = st.integers(0)
optional_int = positive_int | st.just(-1) | st.none()
datetime = st.datetimes().map(lambda d: d.strftime("%Y-%m-%dT%H:%M:%S"))

def timings(t):
    """ Generates TimingsF objects with positive and optional values

    The relation between `ssl` and `connect` is not modeled
    """
    return st.builds(
        TimingsF,
        send=positive_int,
        wait=positive_int,
        receive=positive_int,
        ssl=optional_int,
        connect=optional_int,
        blocked=optional_int,
        dns=optional_int,
        comment=text,
    )

def before_after_request(t):
    return st.builds(
        BeforeAfterRequestF,
        eTag=text,
        expires=datetime,
        lastAccess=datetime,
        hitCount=positive_int,
        comment=text,
    )

