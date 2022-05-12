import json
import logging
from datetime import datetime
from time import sleep

import pandas
import requests
from absl import app, flags
from etherscan import Etherscan

FLAGS = flags.FLAGS
flags.DEFINE_spaceseplist("chains", "eth,ftm", "A list of chains to track", comma_compat=True)
flags.DEFINE_integer("interval", 5, "interval between requests", lower_bound=1)

config = json.load(open("config.json", "r"))
eth = Etherscan(config["eth"]["etherscan"])
ftm_gas_ep = "https://api.ftmscan.com/api?module=gastracker&action=gasoracle&apikey=" + config["ftm"]["ftmscan"]
poly_gas_ep = (
    "https://api.polygonscan.com/api?module=gastracker&action=gasoracle&apikey=" + config["polygon"]["polygonscan"]
)


def track_eth_gas():
    try:
        gas = eth.get_gas_oracle()
        return {
            "chain": "eth",
            "block": int(gas["LastBlock"]),
            "safe": gas["SafeGasPrice"],
            "fast": gas["FastGasPrice"],
            "propose": gas["ProposeGasPrice"],
            "baseFee": gas["suggestBaseFee"],
            "ts": datetime.now().isoformat(timespec="seconds"),
        }
    except:
        logging.warning("etherscan api error")
        return None


def track_L1_gas(chain, ep):
    try:
        resp = requests.get(ep)
        if resp.status_code != 200:
            logging.warning("L1 gas tracker endpoint failure")
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
            eth_gas = track_eth_gas()
            if eth_gas != None:
                gas.append(eth_gas)
        if "ftm" in chains:
            ftm_gas = track_L1_gas("ftm", ftm_gas_ep)
            if ftm_gas != None:
                gas.append(ftm_gas)
        if "polygon" in chains:
            matic_gas = track_L1_gas("matic", poly_gas_ep)
            if matic_gas != None:
                gas.append(matic_gas)
        df = pandas.DataFrame.from_records(data=gas)
        print(df)
        sleep(interval)


if __name__ == "__main__":
    app.run(main)
