import code
from json import dumps
from pprint import pprint

import click
from serde.json import from_json

from harf.core import Har, harf
from harf.correlations import (
    post_data_env,
    header_env,
    content_env,
    response_env,
    request_env,
    entry_env,
    log_env,
    Env,
)


@click.command()
@click.argument("har-file", type=click.File("r"))
@click.option("--interactive", "-i", is_flag=True, default=False)
@click.option("--diffable", "-d", is_flag=True, default=False)
@click.option("--headers", "-h", is_flag=True, default=False)
def correlations(har_file, interactive, diffable, headers):
    # todo: add filters for number of references
    # todo: add verbose to show url instead of entry_{i}
    har = from_json(Har, har_file.read())
    env = harf(
        post_data=post_data_env,
        header=header_env if headers else lambda *a, **k: Env(),
        content=content_env,
        response=response_env,
        request=request_env,
        entry=entry_env,
        log=log_env,
        default=Env(),
    )(har)
    if interactive:
        code.interact(local={"env": env})
    else:
        for p, ps in env.items():
            refs = list(map(str, ps))
            message = f"Value ({repr(p)}) used in:"
            if diffable:
                message = f"Value first seen at {refs[0]} used again in:"
                resfs = refs[1:]
            print(message)
            print(dumps(refs, indent=4).strip("[]\n"))
            print()


if __name__ == "__main__":
    correlations()
