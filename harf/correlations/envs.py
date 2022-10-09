from collections import defaultdict
from functools import partial, reduce
from typing import List, Dict, Callable, TypeVar, Generic
from urllib.parse import urlparse
import base64
import json
import operator

from harf_serde import (
    PostDataTextF,
    QueryStringF,
    HeaderF,
    CookieF,
    ContentF,
    RequestF,
    ResponseF,
    EntryF,
    LogF,
)

from harf.correlations.paths import (
    Path,
    IntPath,
    StrPath,
    EndPath,
    DataPath,
    UrlPath,
    QueryPath,
    HeaderPath,
    CookiePath,
    BodyPath,
    RequestPath,
    ResponsePath,
    EntryPath,
)
from harf.jsonf import jsonf_cata, JsonF, JsonPrims


class Env(Dict[JsonPrims, List[Path]]):
    def map_paths(self, f: Callable[[Path], Path]) -> "Env":
        res = {}
        for p, ps in self.items():
            res[p] = list(map(f, ps))
        return Env(res)

    def __or__(self, other):
        res = defaultdict(list)
        for p, ps in self.items():
            res[p] += ps
        for p, ps in other.items():
            res[p] += ps
        return Env(res)

    def __ior__(self, other):
        return self | other

    def __add__(self, other):
        res = defaultdict(list)
        for value in self:
            res[value] += self[value]
            if value in other:
                res[value] += other[value]
        return Env(res)

    def __sub__(self, other):
        res = defaultdict(list)
        for value in self:
            if value not in other:
                res[value] += self[value]
        return Env(res)


def _json_env(element: JsonF[Env]) -> Env:
    if isinstance(element, dict):
        iter_ = element.items()
        mk_path = StrPath
    elif isinstance(element, list):
        iter_ = enumerate(element)
        mk_path = IntPath
    else:
        return Env({element: [EndPath()]})
    res = Env()
    for path, env in iter_:
        res |= env.map_paths(lambda p: mk_path(path, p))
    return res


json_env = partial(jsonf_cata, _json_env)


def post_data_env(pd: PostDataTextF) -> Env:
    if "application/json" in pd.mimeType:
        text = pd.text
        if text != "":
            return json_env(json.loads(text)).map_paths(BodyPath)
    return Env()


def header_env(h: HeaderF) -> Env:
    if h.name in {"Cookie", "Set-Cookie"}:
        # Cookie related headers should be ignored infavor of dealing with the cookies directly.
        return Env()
    return Env({h.value: [HeaderPath(h.name, EndPath())]})


def cookie_env(c: CookieF) -> Env:
    return Env({c.value: [CookiePath(c.name, EndPath())]})


def query_string_env(q: QueryStringF) -> Env:
    return Env({q.value: [QueryPath(q.name, EndPath())]})


def request_env(r: RequestF[Env, Env, Env, Env]) -> Env:
    url_path = urlparse(r.url).path.strip("/").split("/")
    request_env = r.postData or Env()
    for i, p in enumerate(url_path):
        path = [UrlPath(i, EndPath())]
        if p.isdigit():
            p = int(p)
        if p in request_env:
            request_env[p] = path + request_env[p]
        else:
            request_env[p] = path
    return reduce(
        operator.or_,
        r.cookies,
        reduce(
            operator.or_, r.headers, reduce(operator.or_, r.queryString, request_env)
        ),
    ).map_paths(RequestPath)


def content_env(c: ContentF) -> Env:
    if "application/json" in c.mimeType:
        text = c.text
        if c.encoding == "base64":
            text = base64.b64decode(text)
        if text != "":
            return json_env(json.loads(text)).map_paths(BodyPath)
    return Env()


def response_env(r: ResponseF[Env, Env, Env]) -> Env:
    return reduce(
        operator.or_, r.cookies, reduce(operator.or_, r.headers, r.content)
    ).map_paths(ResponsePath)


def entry_env(e: EntryF[Env, Env, Env, Env]) -> Env:
    return e.request | e.response


def log_env(l: LogF[Env, Env, Env, Env]) -> Env:
    log_env = defaultdict(list)
    for i, entry in enumerate(l.entries):
        for prim, paths in entry.items():
            log_env[prim] += [EntryPath(i, p) for p in paths]
    return Env(log_env)
