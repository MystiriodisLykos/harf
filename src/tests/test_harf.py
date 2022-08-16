from dataclasses import fields, is_dataclass
from inspect import signature
from string import printable
from typing import get_args

from hypothesis import given, infer, strategies as st

from harf.harf import harf, Har, ResponseF, Response, CookieF

text = st.text(printable)

json = st.recursive( st.none() | st.booleans() | st.floats() | text | st.integers(), 
    lambda children: st.lists(children) | st.dictionaries(text, children))

def from_generic_type(t):
    args = get_args(t)
    builders = [st.builds(a) for a in args]
    t = getattr(t, "__origin__", t)
    params = t.__parameters__
    var_builders = dict(zip(params, builders))
    print(var_builders)
    args = {}
    for f in fields(t):
        if f.type in var_builders:
            args[f.name] = var_builders[f.type]
    print(args)
    res = st.builds(t, st.builds(CookieF), st.builds(CookieF))
    return st.none()

st.register_type_strategy(ResponseF, from_generic_type)

@given(default=json, har=infer)
def test_harf_default_is_default(default: int, har: Response):
    assert default == harf(default=default)(har)

test_harf_default_is_default()
