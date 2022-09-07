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


@given(
    alphabet=st.shared(st.sets(json_prims, min_size=1), key="alphabet"),
    json=json(
        prims=st.shared(st.sets(json_prims), key="alphabet")
        .map(list)
        .flatmap(st.sampled_from)
    ),
)
def test_json_with_alphabet_A_makes_env_with_A_or_less(alphabet, json):
    """Creating an env from a json with leaves from alphabet A has at most |A| elements.

    len(A) >= len(env(json(a)))
    """
    env = json_env(json)
    note(env)
    assert len(env) <= len(alphabet)


# test_json_with_alphabet_A_makes_env_with_A_or_less()


@given(
    alphabet=st.shared(st.sets(json_prims, min_size=1), key="alphabet"),
    json=json(
        prims=st.shared(st.sets(json_prims), key="alphabet")
        .map(list)
        .flatmap(st.sampled_from)
    ),
)
@example({False}, False)
def test_json_with_alphabet_A_makes_env_with_values_in_A(alphabet, json):
    env = json_env(json)
    note(env)
    assert set(env).issubset(alphabet)


test_json_with_alphabet_A_makes_env_with_values_in_A()
