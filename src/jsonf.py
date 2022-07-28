from typing import Union, Dict, List, TypeVar, Callable, Tuple

A = TypeVar("A")
B = TypeVar("B")

JSONF = Union[Dict[str, A], List[A], int, str, bool, float, None]
JSON = JSONF["JSON"]

def jsonf_fmap(f: Callable[[A], B], j: JSONF[A]) -> JSONF[B]:
    if isinstance(j, dict):
        return {k: f(v) for k, v in j.items()}
    if isinstance(j, list):
        return [f(e) for e in j]
    return j

def jsonf_cata(a: Callable[[JSONF[A]], A], j: JSON) -> A:
    def inner(e):
        return jsonf_cata(a, e)
    return a(jsonf_fmap(inner, j))

def jsonf_para(a: Callable[[JSONF[Tuple[JSON, A]]], A], j: JSON) -> A:
    def inner(e):
        return jsonf_fmap(lambda x: x[0], e), a(e)
    return jsonf_cata(inner, j)[1]

def jsonf_zygo(h: Callable[[JSONF[B]], B], a: Callable[[JSONF[Tuple[B, A]]], A], j: JSON) -> A:
    def inner(e):
        return h(jsonf_fmap(lambda e: e[0], e)), a(e)
    return jsonf_cata(inner, j)[0]

def json_paths(j: JSON) -> List[str]:
    if isinstance(j, dict):
        iter_ = j.items()
    elif isinstance(j, list):
        iter_ = enumerate(j)
    else:
        return [""]
    return [str(k) + p for k, v in iter_ for p in v]

