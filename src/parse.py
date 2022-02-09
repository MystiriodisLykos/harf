from uuid import uuid4
from typing import Set, Dict, List

from har import Har, Request, Response

from serde.json import from_json

def get_request_values(r: Request) -> Dict[str, str]:
    pass

def get_response_values(r: Response) -> Dict[str, str]:
    pass

def find_replace_request(pattern: str, repl: str, r: Request) -> Request:
    pass

def find_replace_response(pattern: str, repl: str, r: Response) -> Response:
    pass

def connonical_name(value, canidates: Set[str], all_names: Set[str]) -> str:
    pass

def parse(h: Har):
    tracked_values: Dict[str, List[str]] = {}
    for entry in h.log.entries:
        request, response = entry.request, entry.response
        new_values = {**get_request_values(request), **get_response_values(response)}
        for value, name in new_values.items():
            if value in tracked_values:
                tracked_values[value].append(name)
            else:
                tracked_values[value] = [f"httparseId.{uuid4()}", name]
        for value, names in tracked_values.items():
            id = names[0]
            entry.request = find_replace_request(value, id, request)
            entry.response = find_replace_response(value, id, response)
    all_names: Set[str] = set()
    for names in tracked_values.values():
        all_names.union(set(names))
    for entry in h.log.entries:
        for value, names in tracked_values.items():
            id, *names = names
            name = connonical_name(value, set(names), all_names)
            entry.request = find_replace_request(id, name, entry.request)
            entry.response = find_replace_response(id, name, entry.response)

