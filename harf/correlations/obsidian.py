import base64
import colorsys
import textwrap
import json
import pathlib
from dataclasses import dataclass
from functools import partial
from typing import Dict, Union
from itertools import chain
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
    PageF,
    LogF,
    Har,
    harf,
)

from harf.correlations.envs import Env
from harf.jsonf import jsonf_cata, JsonF, JsonPrims

app_json = {
    "livePreview": True,
    "readableLineLength": False,
    "showFrontmatter": True,
    "showLineNumber": True,
    "lineWrap": False,
}
appearance_json = {
    "enabledCssSnippets": ["entry"],
}
graph_json = {
    "collapse-filter": True,
    "search": "",
    "showTags": False,
    "showAttachments": False,
    "hideUnresolved": False,
    "showOrphans": True,
    "collapse-color-groups": True,
    "colorGroups": [],
    "collapse-display": True,
    "showArrow": True,
    "textFadeMultiplier": 0,
    "nodeSizeMultiplier": 1,
    "lineSizeMultiplier": 1,
    "collapse-forces": True,
    "centerStrength": 0.5,
    "repelStrength": 10,
    "linkStrength": 1,
    "linkDistance": 250,
    "scale": 1,
    "close": False,
}

entry_css = """
.request li,
.response li {
    display: inherit;
}

.request ul,
.respones ul {
    padding-inline-start: 2em;
    font-family: monospace;
}
"""


@dataclass(frozen=True)
class FileName:
    name: str


@dataclass(frozen=True)
class VariableName:
    name: str


ObsidianData = Dict[Union[FileName, VariableName], str]


class ReservedVariables:
    query_string = VariableName("query_string")
    post_data = VariableName("post_data")
    url = VariableName("url")
    content = VariableName("content")
    page_id = VariableName("page_id")
    request = VariableName("request")
    response = VariableName("response")
    comment = VariableName("comment")


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


def post_data(env: Env, pd: PostDataTextF) -> ObsidianData:
    if pd.mimeType == "application/json":
        text = pd.text
        if text != "":
            return {ReservedVariables.post_data: json_(env, json.loads(pd.text))}
    return {}


def query_string(env: Env, qs: QueryStringF) -> ObsidianData:
    return {ReservedVariables.query_string: f"{qs.name}: {_get_link(env, qs.value)}"}


def request(
    env: Env, r: RequestF[ObsidianData, ObsidianData, ObsidianData, ObsidianData]
) -> ObsidianData:
    obsidian_data = {}

    url = urlparse(r.url).path.strip("/").split("/")
    f_url = "/"
    for p in url:
        if p.isdigit():
            p = int(p)
        f_url += _get_link(env, p).strip("'\"") + "/"

    query_string = ""
    post_data = r.postData if r.postData is not None else {}
    for type_, value in chain(
        post_data.items(), *map(lambda q: q.items(), r.queryString)
    ):
        if type_ == ReservedVariables.query_string:
            query_string += f"- {value}\n"
        else:
            obsidian_data[type_] = value

    obsidian_data[ReservedVariables.query_string] = query_string
    obsidian_data[ReservedVariables.url] = f"{r.method.upper()} {f_url.strip('/')}"
    return obsidian_data


def content(env: Env, c: ContentF) -> ObsidianData:
    if "application/json" in c.mimeType:
        text = c.text
        if c.encoding == "base64":
            text = base64.b64decode(text)
        if text != "":
            return {ReservedVariables.content: json_(env, json.loads(text))}
    return {}


def response(
    env: Env, r: ResponseF[ObsidianData, ObsidianData, ObsidianData]
) -> ObsidianData:
    return r.content


def entry(
    env: Env, e: EntryF[ObsidianData, ObsidianData, ObsidianData, ObsidianData]
) -> ObsidianData:
    obsidian_data = {}

    request = f"---\ncssclass: request\ntags: [{e.pageref}]\n---\n"
    url = None
    post_data = None
    query_string = None
    for type_, value in e.request.items():
        if type_ == ReservedVariables.url:
            url = value
        elif type_ == ReservedVariables.post_data:
            post_data = value
        elif type_ == ReservedVariables.query_string:
            query_string = value
        else:
            obsidian_data[type_] = value

    if url:
        request += f"# {url}\n"
    if e.comment:
        request += f"{e.comment}\n"
    if query_string:
        request += f"\n## Query String\n{query_string}\n"
    if post_data:
        request += f"\n## Body Data\n{post_data}\n"

    response = f"---\ncssclass: response\ntags: [{e.pageref}]\n---\n\n## Body Data\n"
    response_data = None
    for type_, value in e.response.items():
        if type_ == ReservedVariables.content:
            response_data = value
        else:
            obsidian_data[type_] = value
    if response_data:
        response += response_data
    else:
        response += "No response data"

    obsidian_data[ReservedVariables.request] = request
    obsidian_data[ReservedVariables.response] = response
    return obsidian_data


def page(env: Env, p: PageF[ObsidianData]) -> ObsidianData:
    return {ReservedVariables.page_id: p.id}


def log(
    env: Env, e: LogF[ObsidianData, ObsidianData, ObsidianData, ObsidianData]
) -> ObsidianData:
    obsidian_data = {}
    request_responses = {}
    for i, entry in enumerate(e.entries):
        request = None
        response = None
        for type_, value in entry.items():
            if type_ == ReservedVariables.request:
                request = value
            elif type_ == ReservedVariables.response:
                response = value
            else:
                obsidian_data[type_] = value
        if request:
            if response:
                request += f"\n# Response\n![[response_{i}]]\n"
            request_responses[FileName(f"request_{i}.md")] = request
        if response:
            request_responses[FileName(f"response_{i}.md")] = response

    graph = {**graph_json}

    color_groups = []
    for i, page in enumerate(e.pages):
        hue = i / len(e.pages) * (33 / 36)
        r, g, b = colorsys.hsv_to_rgb(hue, 1.0, 1.0)
        page_id = None
        for type_, value in page.items():
            if type_ == ReservedVariables.page_id:
                page_id = value
            else:
                obsidian_data[type_] = value
        if page_id:
            color_groups.append(
                {
                    "query": f"tag({page_id})",
                    "color": {
                        "a": 1,
                        "rgb": (int(r * 255) << 16)
                        + (int(g * 255) << 8)
                        + int(b * 255),
                    },
                }
            )
    graph["colorGroups"] = color_groups

    vault_settings = {
        FileName(".obsidian/app.json"): json.dumps(app_json),
        FileName(".obsidian/appearance.json"): json.dumps(appearance_json),
        FileName(".obsidian/graph.json"): json.dumps(graph),
        FileName(".obsidian/snippets/entry.css"): entry_css,
    }
    return {**obsidian_data, **request_responses, **vault_settings}


def mk_obsidian(env: Env, h: Har) -> ObsidianData:
    return harf(
        post_data=partial(post_data, env),
        querystring=partial(query_string, env),
        request=partial(request, env),
        content=partial(content, env),
        response=partial(response, env),
        entry=partial(entry, env),
        page=partial(page, env),
        log=partial(log, env),
        default={},
    )(h)


def write_files(od: ObsidianData, root: pathlib.Path) -> None:
    for type_, value in od.items():
        if isinstance(type_, FileName):
            with open(root / pathlib.Path(type_.name), "w") as file:
                file.write(value)
        else:
            print("Unused thing", type_, value)
