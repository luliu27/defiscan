# defiscan

A set of tools to investigate defi.

## Installtion

Before proceeding, you should register an account on

- [Etherscan.io](https://etherscan.io/) and [generate a personal API key](https://etherscan.io/myapikey) to use
- [Etherscan.io](https://etherscan.io/) and [generate a personal API key](https://etherscan.io/myapikey) to use
- [Infura.io](ttps://infura.io/), create a project, and get project ID to use

Install from source:

```bash
# suggest use venv to set up virtual env
python3 -m pip install --user virtualenv

git clone git@github.com:luliu27/defiscan.git

cd defiscan
# install virtual env for the project
python3 -m venv venv
# activate the virtual env
source venv/bin/activate
# install dependencies
python3 -m pip install -r requirements.txt
```

## Utilities

```bash
# set up config.json and update API keys in the file
cp config.json.sample config.json
# run gas tracker
python3 gas_tracker.py --chains eth,ftm

# TODO: dex tracker
# TODO: support more L1 chains
# more to come
```
