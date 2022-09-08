from dataclasses import fields, is_dataclass
from functools import partial
from inspect import signature
from itertools import chain
from string import printable
from typing import get_args, TypeVar, List

from hypothesis import assume, example, given, infer, note, strategies as st

from harf.core import harf, Har, ResponseF, Response, CookieF
from harf.correlations import mk_env, json_env
from harf.jsonf import jsonf_cata

from strategies import json_prims, json


def _json_depth_a(json) -> int:
    if isinstance(json, (list, dict)):
        values = json if isinstance(json, list) else json.values()
        return max(filter(lambda x: x > 0, values), default=-1) + 1
    return 1


json_depth = partial(jsonf_cata, _json_depth_a)

max_path_length = lambda env: max(map(len, chain(*env.values())), default=0)


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


# test_json_with_alphabet_A_makes_env_with_values_in_A()


@given(json=json())
@example(None)
@example([])
@example({})
@example([[]])
def test_max_env_equals_json_depth(json):
    env = json_env(json)
    note(env)
    depth = json_depth(json)
    note(depth)
    max_path = max_path_length(env)
    note(max_path)
    assert depth == max_path


# test_max_env_equals_json_depth()


@given(json=json())
def test_building_nested_json_from_json_does_not_change_values(json):
    env = json_env(json)
    note(env)
    assert list(env) == list(json_env([json, json]))
    assert list(env) == list(json_env({"a": json, "b": json}))


# test_building_nested_json_from_json_does_not_change_values()


@given(json=json(min_size=1))
def test_building_nested_json_from_json_increases_max_path_by_one(json):
    env = json_env(json)
    note(env)
    assert max_path_length(env) + 1 == max_path_length(json_env([json, json]))
    assert max_path_length(env) + 1 == max_path_length(json_env({"A": json, "B": json}))


test_building_nested_json_from_json_increases_max_path_by_one()
