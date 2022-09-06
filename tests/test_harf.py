from dataclasses import fields, is_dataclass
from inspect import signature
from string import printable
from typing import get_args, TypeVar, List

from hypothesis import assume, example, given, infer, note, strategies as st

from harf.core import harf, Har, ResponseF, Response, CookieF
from harf.correlations import mk_env, json_env

from strategies import json_prims, json

@given(json=json_prims.flatmap(lambda e: json(prims=st.just(e), min_size=1)))
@example(None)
def test_jsonn_with_single_prim_makes_env_with_single_entry(json):
    env = json_env(json)
    note(env)
    assert len(env) == 1


# test_jsonn_with_single_prim_makes_env_with_single_entry()

"""
@given(alphabet=st.shared(st.sets(json_prims), key="alphabet"),json=json(prims=st.shared(st.sets(json_prims), key="alphabet").flat_map(lambda e: st.sampled_from(list(e)))))
def test_json_with_alphabet_A_makes_env_with_A_or_less(alphabet, json):
    note(alphabet)
    note(json)
    assert len(alphabet) < 3
"""
# test_json_with_alphabet_A_makes_env_with_A_or_less()

print(json(st.sets(st.integers())).example())

