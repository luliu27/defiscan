import json
import logging
from datetime import datetime
from time import sleep

import pandas
import requests
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


def track_L1_gas(chain):
    try:
        resp = requests.get(chain_eps[chain])
        if resp.status_code != 200:
            logging.warning("{} gas tracker endpoint failure".format(chain))
            return None
        gas = json.loads(resp.text)["result"]
        return {
            "chain": chain,
            "block": int(gas["LastBlock"]),
            "safe": gas["SafeGasPrice"],
            "fast": gas["FastGasPrice"],
            "propose": gas["ProposeGasPrice"],
            "baseFee": gas["suggestBaseFee"] if "suggestBaseFee" in gas else "0.0",
            "ts": datetime.now().isoformat(timespec="seconds"),
        }
    except Exception as e:
        logging.warning("{} api error: {}".format(chain, e))
        return None


def main(_):
    chains = FLAGS.chains
    interval = FLAGS.interval

    if not chains:
        logging.warning("no chain specified")
        exit

    while True:
        gas = []
        if "eth" in chains:
            eth_gas = track_L1_gas("eth")
            if eth_gas != None:
                gas.append(eth_gas)
        if "ftm" in chains:
            ftm_gas = track_L1_gas("ftm")
            if ftm_gas != None:
                gas.append(ftm_gas)
        if "polygon" in chains:
            matic_gas = track_L1_gas("polygon")
            if matic_gas != None:
                gas.append(matic_gas)
        df = pandas.DataFrame.from_records(data=gas)
        print(df)
        sleep(interval)


if __name__ == "__main__":
    app.run(main)
