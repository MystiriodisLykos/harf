from dataclasses import fields, is_dataclass
from inspect import signature
from string import printable
from typing import get_args, TypeVar, List

from hypothesis import given, infer, strategies as st

from harf.harf import harf, Har, ResponseF, Response, CookieF

text = st.text(printable)

json = st.recursive( st.none() | st.booleans() | st.floats() | text | st.integers(), 
    lambda children: st.lists(children) | st.dictionaries(text, children))

def from_generic_type(t):
    args = get_args(t)
    print(t)
    print(args)
    print(dir(t))
    builders = [st.builds(a) for a in args]
    t = getattr(t, "__origin__", t)
    params = t.__parameters__
    var_arg = dict(zip(params, args))
    builder_args = {}
    for f in fields(t):
        if f.type in var_arg:
            builder_args[f.name] = st.builds(var_arg[f.type])
        elif hasattr(f.type, "__origin__"):
            inner_args = [var_arg.get(v, v) for v in get_args(f.type) if isinstance(v, TypeVar)]
            if inner_args:
                builder_args[f.name] = from_generic_type(f.type.__getitem__(*inner_args))
        else:
            builder_args[f.name] = st.builds(f.type)
    print(builder_args)
    return st.builds(t, **builder_args) 

#st.register_type_strategy(ResponseF, from_generic_type)

#@given(default=json, har=infer)
def test_harf_default_is_default(default: int, har: Response):
    assert default == harf(default=default)(har)
    pass

#test_harf_default_is_default()
# print(st.builds(List[int]).example())
print(from_generic_type(Response).example())
