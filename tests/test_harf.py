from dataclasses import fields, is_dataclass
from inspect import signature
from string import printable
from typing import get_args, TypeVar, List

from hypothesis import assume, given, infer, note, strategies as st

from harf.core import harf, Har, ResponseF, Response, CookieF
from harf.correlations import mk_env, json_env

text = st.text(printable)

json_prims = st.none() | st.booleans() | st.floats() | text | st.integers()


@st.composite
def json(draw, prims=json_prims, keys=text, min_size=0, max_size=None):
    return draw(
        st.recursive(
            prims,
            lambda children: st.lists(children, min_size=min_size, max_size=max_size)
            | st.dictionaries(keys, children, min_size=min_size, max_size=max_size),
        )
    )


@given(json=json_prims.flatmap(lambda e: json(prims=st.just(e), min_size=1)))
def test_jsonn_with_single_prim_makes_env_with_single_entry(json):
    env = json_env(json)
    note(env)
    assert len(env) == 1


test_jsonn_with_single_prim_makes_env_with_single_entry()

# @given(default=json, har=infer)
def test_harf_default_is_default(default: int, har: Response):
    assert default == harf(default=default)(har)
    pass
