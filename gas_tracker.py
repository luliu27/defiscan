import asyncio
import json
import logging
from datetime import datetime
from time import sleep

import aiohttp
import pandas
from absl import app, flags

FLAGS = flags.FLAGS
flags.DEFINE_spaceseplist("chains", "eth,ftm", "A list of chains to track", comma_compat=True)
flags.DEFINE_integer("interval", 5, "interval between requests", lower_bound=1)

config = json.load(open("config.json", "r"))
chain_eps = {
    "eth": "https://api.etherscan.io/api?module=gastracker&action=gasoracle&apikey=" + config["eth"]["etherscan"],
    "ftm": "https://api.ftmscan.com/api?module=gastracker&action=gasoracle&apikey=" + config["ftm"]["ftmscan"],
    "polygon": "https://api.polygonscan.com/api?module=gastracker&action=gasoracle&apikey="
    + config["polygon"]["polygonscan"],
}


async def track_l1_gas(session: aiohttp.ClientSession, chain: str, **kwargs) -> dict:
    resp = await session.request("GET", url=chain_eps[chain], **kwargs)
    if resp.status != 200:
        logging.warning("{} gas tracker EP failure".format(chain))
        return None
    data = await resp.json()
    gas = data["result"]
    return {
        "chain": chain,
        "block": int(gas["LastBlock"]),
        "safe": gas["SafeGasPrice"],
        "fast": gas["FastGasPrice"],
        "propose": gas["ProposeGasPrice"],
        "baseFee": gas["suggestBaseFee"] if "suggestBaseFee" in gas else "0.0",
        "ts": datetime.now().isoformat(timespec="seconds"),
    }


async def track(chains, **kwargs):
    async with aiohttp.ClientSession() as session:
        tasks = []
        for chain in chains:
            tasks.append(track_l1_gas(session=session, chain=chain, **kwargs))
        gas = await asyncio.gather(*tasks, return_exceptions=False)
        return gas


def main(_):
    chains = FLAGS.chains
    interval = FLAGS.interval

    if not chains:
        logging.warning("no chain specified")
        exit

    while True:
        results = asyncio.run(track(chains))
        gas = list(filter(None, results))
        df = pandas.DataFrame.from_records(data=gas)
        print(df)
        sleep(interval)


if __name__ == "__main__":
    app.run(main)
