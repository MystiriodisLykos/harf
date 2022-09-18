from functools import partial
from itertools import chain
from json import dumps as json_dumps

from hypothesis import assume, example, given, infer, note, strategies as st

from harf.core import (
    harf,
    CookieF,
    HeaderF,
    PostDataTextF,
    QueryStringF,
)
from harf.correlations.envs import (
    json_env,
    EndPath,
    HeaderPath,
    CookiePath,
    QueryPath,
    header_env,
    post_data_env,
    cookie_env,
    query_string_env,
)
from harf.jsonf import jsonf_cata

from strategies import json_prims, json, text, post_data_text


def _json_depth_a(json) -> int:
    if isinstance(json, (list, dict)):
        values = json if isinstance(json, list) else json.values()
        return max(filter(lambda x: x > 0, values), default=-1) + 1
    return 1


json_depth = partial(jsonf_cata, _json_depth_a)

paths = lambda env: chain(*env.values())
max_path_length = lambda env: max(map(len, paths(env)), default=0)


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


# test_building_nested_json_from_json_increases_max_path_by_one()


@given(json=json(min_size=1))
def test_building_nested_json_from_json_doubles_number_of_paths(json):
    env = json_env(json)
    note(env)
    assert len(list(paths(env))) * 2 == len(list(paths(json_env([json, json]))))
    assert len(list(paths(env))) * 2 == len(
        list(paths(json_env({"A": json, "B": json})))
    )


# test_building_nested_json_from_json_doubles_number_of_paths()


@given(
    alphabet=st.shared(st.sets(json_prims, min_size=1), key="alphabet"),
    json=json(
        prims=st.shared(st.sets(json_prims), key="alphabet")
        .map(list)
        .flatmap(st.sampled_from)
    ),
    extra=json_prims,
)
def test_adding_an_extra_value_to_json_increases_values_and_paths_by_one(
    alphabet, json, extra
):
    assume(extra not in alphabet)
    env = json_env(json)
    note(env)
    envl = json_env([json, extra])
    envd = json_env({"J": json, "E": extra})
    note(envl)
    note(envd)
    assert len(env) + 1 == len(envl) == len(envd)
    assert len(list(paths(env))) + 1 == len(list(paths(envl))) == len(list(paths(envd)))


# test_adding_an_extra_value_to_json_increases_values_and_paths_by_one()


@given(json=json())
def test_nesting_json_once_does_not_change_values_or_path_count(json):
    env = json_env(json)
    note(env)
    envl = json_env([json])
    envd = json_env({"id": json})
    note(envl)
    note(envd)
    assert list(env) == list(envl) == list(envd)
    assert len(list(paths(env))) == len(list(paths(envl))) == len(list(paths(envd)))


# test_nesting_json_once_does_not_change_values_or_path_count()


@given(
    json=json(
        prims=(
            st.lists(json_prims, min_size=1)
            | st.dictionaries(text, json_prims, min_size=1)
        ),
        min_size=1,
    )
)
@example({"": [None, None]})
@example([None])
def test_the_number_of_paths_is_the_sum_of_all_sub_envs(json):
    env = json_env(json)
    note(env)
    path_count = len(list(paths(env)))
    note(path_count)
    values = json if isinstance(json, list) else json.values()
    assert path_count == sum(len(list(paths(json_env(s)))) for s in values)


# test_the_number_of_paths_is_the_sum_of_all_sub_envs()


@given(
    json=json(
        prims=(
            st.lists(json_prims, min_size=1)
            | st.dictionaries(text, json_prims, min_size=1)
        ),
        min_size=1,
    )
)
def test_the_set_of_values_is_the_inclusion_of_all_sub_values(json):
    env = json_env(json)
    note(env)
    values = json if isinstance(json, list) else json.values()
    assert set(env.keys()) == set(chain(*[json_env(s).keys() for s in values]))


# test_the_set_of_values_is_the_inclusion_of_all_sub_values()


@given(json=json_prims)
def test_primitive_values_produce_primative_env(json):
    env = json_env(json)
    note(env)
    assert len(env) == 1
    env_paths = list(paths(env))
    assert len(env_paths) == 1
    assert env_paths == [EndPath()]


# test_primitive_values_produce_primative_env()


@given(header=infer)
def test_header_env_makes_a_single_env(header: HeaderF):
    env = header_env(header)
    note(env)
    assert len(env) == 1
    assert header.value in env
    assert len(env[header.value]) == 1
    assert isinstance(env[header.value][0], HeaderPath)


@given(cookie=infer)
def test_cookie_env_makes_a_single_env(cookie: CookieF):
    env = cookie_env(cookie)
    note(env)
    assert len(env) == 1
    assert cookie.value in env
    assert len(env[cookie.value]) == 1
    assert isinstance(env[cookie.value][0], CookiePath)

@given(query_string=infer)
def test_query_string_env_makes_a_single_env(query_string: QueryStringF):
    env = query_string_env(query_string)
    note(env)
    assert len(env) == 1
    assert query_string.value in env
    assert len(env[query_string.value]) == 1
    assert isinstance(env[query_string.value][0], QueryPath)


@given(
    json=st.shared(json(), key="json"),
    post_data=post_data_text(
        mime_data=st.tuples(
            st.just("application/json"), st.shared(json(), key="json").map(json_dumps)
        )
    ),
)
def test_post_data_env_is_equivalent_to_json_env(json, post_data):
    jenv = json_env(json)
    penv = post_data_env(post_data)
    assert len(jenv) == len(penv)
    assert set(jenv) == set(penv)
    for v, rs in penv.items():
        assert len(jenv[v]) == len(rs)
        for j, p in zip(jenv[v], rs):
            assert p.next_ == j
