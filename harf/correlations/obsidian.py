import textwrap
import json
from functools import partial
from urllib.parse import urlparse

from harf.core import (
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

from harf.correlations.envs import Env
from harf.jsonf import jsonf_cata, JsonF, JsonPrims

def _get_link(env: Env, value: JsonPrims) -> str:
    alias = repr(value)
    if value in env:
        return f"[[{str(env[value][0])}|{alias}]]"
    return alias

def _json_str(env: Env, element: JsonF[str]) -> str:
    if isinstance(element, dict):
        res = "- \\{\n"
        for k, v in element.items():
            res += textwrap.indent(f"- {repr(k)}: {v}", " "*4) + "\n"
        return res + "- \\}"
    elif isinstance(element, list):
        res = "- \\[\n"
        for e in element:
            res += textwrap.indent("- " + e, " "*4) + "\n"
        return res + "- \\]"
    else:
        return _get_link(env, element)

def json_(env: Env, element: JsonF) -> str:
    return jsonf_cata(partial(_json_str, env), element)

def post_data(env: Env, pd: PostDataTextF) -> str:
    return json_(env, json.loads(pd.text))

def query_string(env: Env, qs: QueryStringF) -> str:
    return f"{qs.name}: {_get_link(env, qs.value)}"

def request(env: Env, r: RequestF[str, str, str, str]) -> str:
    url = urlparse(r.url).path.strip("/").split("/")
    f_url = "/"
    for p in url:
        f_url += _get_link(env, p) + "/"
    query_string = ""
    if len(r.queryString) != 0:
        query_string = "- " + "\n- ".join(r.queryString)
    return f"""---
cssclass: request
---

# {upper(r.method)} {f_url.rstrip('/')}
{request.comment if request.comment else ""}

## QueryString
{query_string if query_string else "None"}

---

## Body
{r.postData if r.postData else "None"}
"""
