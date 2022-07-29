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
    return jsonf_cata(inner, j)[1]

def json_paths(j: JSONF[List[str]]) -> List[str]:
    if isinstance(j, dict):
        iter_ = j.items()
    elif isinstance(j, list):
        iter_ = enumerate(j)
    else:
        return [""]
    res = []
    for p, ns in iter_:
        s = [str(p) + p_ for p_ in ns]
        res += s
    return res

def to_values(ns: List[str]) -> Dict[str, List[str]]:
    "We don't have acess to the actual values here"
    pass

def json_correlations_(j: JSONF[Dict[str, List[str]]]) -> Dict[str, List[str]]:
    """ What function do I need to turn json_paths into this?
    json_paths :: JsonF [String] -> [String]
    json_correlations :: JsonF {Prim, [String]} -> {Prim, [String]}
    _ :: Prim -> [String] -> {Prim, [String]}
      :: b -> a -> {b, a}
    """
    if isinstance(j, dict):
        iter_ = j.items()
    elif isinstance(j, list):
        iter_ = enumerate(j)
    else:
        return {j: [""]}
    res = {}
    for p, d in iter_:
        for k, v in d.items():
            u = [str(p) + p_ for p_ in v]
            if k in res:
                res[k] += u
            else:
                res[k] = u
    return res

example = {
    "a" : 1,
    "bs": [2, 3],
    "cs": [4, 6],
    "ds": [
        {"x": 7},
        {"y": 1}
    ]
}
print(example)
print(jsonf_cata(json_correlations_, example))
