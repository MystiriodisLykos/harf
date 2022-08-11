import code
from json import dumps
from pprint import pprint

import click
from serde.json import from_json

from harf.harf import Har
from harf.correlations import mk_env

@click.command()
@click.argument("har-file", type=click.File('r'))
@click.option("--interactive", "-i", is_flag=True, default=False)
def correlations(har_file, interactive):
    har = from_json(Har, har_file.read())
    env = mk_env(har)
    if interactive:
        code.interact(local={"env": env})
    else:
        for p, ps in env.items():
            print(f"Value ({repr(p)}) used in:")
            print(dumps(list(map(str, ps)), indent=4).strip("[]\n"))
            print()

if __name__ == "__main__":
    correlations()
