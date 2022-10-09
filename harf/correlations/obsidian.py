import textwrap
import json
from functools import partial
from urllib.parse import urlparse

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
    Har,
    harf,
)

from harf.correlations.envs import Env
from harf.jsonf import jsonf_cata, JsonF, JsonPrims


def _get_link(env: Env, value: JsonPrims) -> str:
    if value in env:
        link = str(env[value][0]).replace("[", "_").replace("]", "")
        link = f"[[{link}|{value}]]"
        if "'" in repr(value):
            return f'"{link}"'
        return link
    return repr(value)


def _json_str(env: Env, element: JsonF[str]) -> str:
    if isinstance(element, dict):
        res = "- \\{\n"
        for k, v in element.items():
            key = repr(k).replace("'", '"')
            res += textwrap.indent(f"- {key}: {v.lstrip('- ')}", " " * 4) + "\n"
        return res + "- \\}"
    elif isinstance(element, list):
        res = "- \\[\n"
        for e in element:
            res += textwrap.indent("- " + e.lstrip("- "), " " * 4) + "\n"
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
        if p.isdigit():
            p = int(p)
        f_url += _get_link(env, p).strip("'\"") + "/"
    query_string = ""
    if len(r.queryString) != 0:
        query_string = "- " + "\n- ".join(r.queryString)
    return f"""---
cssclass: request
---

# {r.method.upper()} {f_url.rstrip('/')}
{r.comment if r.comment else ""}

## QueryString
{query_string if query_string else "None"}

---

## Body
{r.postData if r.postData else "None"}
"""


def content(env: Env, c: ContentF) -> str:
    if "application/json" in c.mimeType:
        text = c.text
        if c.encoding == "base64":
            text = base64.b64decode(text)
        if text != "":
            return json_(env, json.loads(text))
    return ""


def response(env: Env, r: ResponseF[str, str, str]) -> str:
    return f"""---
cssclass: response
---

## Body
{r.content if r.content else "None"}
"""


def entry(env: Env, e: EntryF[str, str, str, str]) -> str:
    return f"""{e.request}

## Page
![[{e.pageref}]]

{e.response}
"""


def log(env: Env, e: LogF[str, str, str, str]) -> str:
    return "\n__ENTRY\n".join(e.entries)


def mk_obsidian(env: Env, h: Har) -> str:
    return harf(
        post_data=partial(post_data, env),
        querystring=partial(query_string, env),
        request=partial(request, env),
        content=partial(content, env),
        response=partial(response, env),
        entry=partial(entry, env),
        log=partial(log, env),
        default="",
    )(h)
