from base64 import b64decode
from dataclasses import replace
from functools import partial
from itertools import chain
from uuid import uuid4
from typing import Set, Dict, List
from re import sub, match

import json

from har import Har, Request, Response

from serde.json import from_json

def get_request_values(r: Request) -> Dict[str, str]:
    m = match("https://gorest.co.in/public/v2/users/(\d+)", r.url)
    if m:
        return {m.group(1): "userId"}
    return {}

def get_response_values(r: Response) -> Dict[str, str]:
    text = r.content.text
    if text:
        data = json.loads(text)
        if type(data) == list:
            return {e["id"]: "id" for e in data}
        return {data["id"]: "id"}
    return {}

def find_replace_request(pattern: str, repl: str, r: Request) -> Request:
    replace_re = partial(sub, pattern, repl)
    postData = r.postData
    if postData:
        postData = replace(
            postData,
            text=replace_re(postData.text)
        )
    return replace(
        r,
        url=replace_re(r.url),
        queryString=[replace(q, value=replace_re(q.value)) for q in r.queryString],
        postData=postData
    )

def find_replace_response(pattern: str, repl: str, r: Response) -> Response:
    replace_re = partial(sub, pattern, repl)
    if r.content.text:
        return replace(
            r,
            content=replace(r.content, text=replace_re(r.content.text))
        )
    return r

def connonical_name(value, canidates: Set[str], all_names: Set[str]) -> str:
    if len(canidates) > 1:
        return f"[[{list(canidates-set(['id']))[0]}]]"
    return value

def parse(h: Har):
    tracked_values: Dict[str, List[str]] = {}
    for entry in h.log.entries:
        request, response = entry.request, entry.response
        if response.content.encoding == "base64":
            response.content = replace(response.content, text=b64decode(response.content.text).decode("utf-8"))
        new_request_values = get_request_values(request)
        new_response_values = get_response_values(response)
        for value, name in chain(new_request_values.items(), new_response_values.items()):
            value = str(value)
            if value in tracked_values:
                tracked_values[value].append(name)
            else:
                tracked_values[value] = [f"httparseId.{uuid4()}", name]
        for value, names in tracked_values.items():
            id = names[0]
            request = find_replace_request(value, id, request)
            response = find_replace_response(value, id, response)
        entry.request = request
        entry.response = response
    all_names: Set[str] = set()
    for names in tracked_values.values():
        all_names |= set(names[1:])
    for entry in h.log.entries:
        for value, names in tracked_values.items():
            id, *names = names
            name = connonical_name(value, set(names), all_names)
            entry.request = find_replace_request(id, name, entry.request)
            entry.response = find_replace_response(id, name, entry.response)

if __name__ == "__main__":
    from serde.json import from_json
    with open("./test/gorest_demo.har") as file:
        har = from_json(Har, file.read())
        parse(har)
        from pprint import pprint
        pprint(har.log.entries[1].response.content.text)
