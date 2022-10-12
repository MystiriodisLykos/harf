import code
import colorsys
import glob
import shutil
import pathlib
from functools import partial
from itertools import chain
from importlib import resources
from json import dumps, load, dump
from typing import Callable
from pprint import pprint

import click
from serde.json import from_json
from harf_serde import Har, harf

from harf.correlations.envs import (
    post_data_env,
    header_env,
    cookie_env,
    query_string_env,
    content_env,
    response_env,
    request_env,
    entry_env,
    log_env,
    Env,
    Path,
)
from harf.correlations.obsidian import mk_obsidian, write_files
from harf.grouping.by_comment import icomment_requests


def filter_by_percentages(min_percent: float, max_percent: float, env: Env) -> Env:
    max_reference_count = len(max(env.values(), key=len))
    min_bound = int(max_reference_count * min_percent)
    max_bound = int(max_reference_count * max_percent)
    filtered_env = Env()
    for v, ps in env.items():
        if min_bound <= len(ps) <= max_bound:
            filtered_env[v] = ps
    return filtered_env


def str_env(
    env: Env, verbose=False, diffable=False, str_ref: Callable[[Path], str] = str
) -> str:
    res = ""
    for p, ps in env.items():
        refs = list(map(str_ref, ps))
        message = f"Value ({repr(p)}) used in:"
        if diffable:
            if len(refs) == 1:
                continue
            message = f"Value first seen at {refs[0]} used again in:"
            refs = refs[1:]
        res += f"{message}\n"
        res += dumps(refs, indent=4).strip("[]").lstrip("\n")
        res += "\n"
    return res


def request_valued_env(har: Har, headers: bool = False, cookies: bool = False) -> Env:
    return harf(
        post_data=post_data_env,
        header=header_env if headers else None,
        cookie=cookie_env if cookies else None,
        querystring=query_string_env,
        request=request_env,
        entry=entry_env,
        log=log_env,
        default=Env(),
    )(har)


def response_valued_env(har: Har, headers: bool = False, cookies: bool = False) -> Env:
    return harf(
        header=header_env if headers else None,
        cookie=cookie_env if cookies else None,
        content=content_env,
        response=response_env,
        entry=entry_env,
        log=log_env,
        default=Env(),
    )(har)


@click.command()
@click.argument("har-file", type=click.File("r", encoding="utf-8-sig"))
@click.option(
    "--interactive",
    "-i",
    is_flag=True,
    default=False,
    help="Starts an interactive python shell with the har file and env loaded.",
)
@click.option(
    "--diffable",
    "-d",
    is_flag=True,
    default=False,
    help="Replaces values in reference strings to help with diffing between har files.",
)
@click.option(
    "--headers",
    "-h",
    is_flag=True,
    default=False,
    help="Inspect headers for correlation values.",
    show_default=True,
)
@click.option(
    "--cookies",
    "-c",
    is_flag=True,
    default=False,
    help="Inspect cookies for correlation values.",
    show_default=True,
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    default=False,
    help="Make the output slightly more verbose by using the full url when available instead of entry number.",
)
@click.option(
    "--min-reference-percent", "-m", "min_percent", default=2, show_default=True
)
@click.option(
    "--max-reference-percent", "-x", "max_percent", default=98, show_default=True
)
@click.option("--obsidian", "-o", type=click.Path(file_okay=False))
def correlations(
    har_file,
    interactive,
    diffable,
    headers,
    cookies,
    verbose,
    min_percent,
    max_percent,
    obsidian,
):
    har = from_json(Har, har_file.read())
    icomment_requests(har.log)
    request_values = request_valued_env(har)
    response_values = response_valued_env(har)
    env = request_values + response_values
    if interactive:
        code.interact(
            local={
                "env": env,
                "har": har,
                "filter_env": partial(
                    filter_by_percentages, min_percent / 100, max_percent / 100
                ),
                "str_env": str_env,
                "unused_values": response_values - request_values,
            }
        )
        return
    if min_percent > 0 or max_percent < 100:
        env = filter_by_percentages(min_percent / 100, max_percent / 100, env)
    if verbose:
        to_ref = (
            lambda p: har.log.entries[p.index].request.url
            + " "
            + str(p.next_).lstrip(".")
        )
    else:
        to_ref = str
    if obsidian:
        obsidian = pathlib.Path(obsidian)
        out_dir = obsidian / pathlib.Path(har_file.name).stem
        (out_dir / ".obsidian" / "snippets").mkdir(parents=True, exist_ok=True)
        obsidian_data = mk_obsidian(env, har)
        write_files(obsidian_data, out_dir)
    else:
        print(str_env(env, verbose, diffable, to_ref))


if __name__ == "__main__":
    correlations()
