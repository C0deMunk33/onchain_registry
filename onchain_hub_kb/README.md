

Deploy:
onchain_registry/npx hardhat node
onchain_registry/npx hardhat run --network localhost scripts/deploy.js
onchain_hub_kb/poetry run python groupchat_kb/run.py

Must deploy contract to network and update .env with the path to deployed-contract.json (a dict with address and abi). The example .env is setup for the current setup