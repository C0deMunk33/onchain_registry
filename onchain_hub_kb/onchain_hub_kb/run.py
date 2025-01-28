#!/usr/bin/env python
from dotenv import load_dotenv
from onchain_hub_kb.schemas import InputSchema
import random
from typing import Dict, Any
from naptha_sdk.schemas import KBRunInput, KBDeployment
from naptha_sdk.storage.storage_provider import StorageProvider
from naptha_sdk.user import sign_consumer_id
from naptha_sdk.utils import get_logger

import json
import io

from web3 import Web3

import naptha_sdk.storage.schemas as schemas
from typing import List
load_dotenv()

logger = get_logger(__name__)

# You can create your module as a class or function
class OnchainHubKB:
    def __init__(self, deployment: Dict[str, Any]):
        self.deployment = deployment
        self.config = self.deployment.config
        self.storage_provider = StorageProvider(self.deployment.node)
        self.storage_type = self.config.storage_type
        self.table_name = self.config.path
        self.schema = self.config.schema

        # check that directories folder exists, make it if it doesn't
        os.makedirs("directories", exist_ok=True)
        eth_url = os.getenv("ETH_NODE_URL")
        self.w3 = Web3(Web3.HTTPProvider(eth_url))
        registry_deployment_file = os.getenv("REGISTRY_DEPLOYMENT_FILE")

        with open(registry_deployment_file, "r") as f:
            self.deployed_contract = json.load(f)

        self.contract_address = self.deployed_contract["address"]
        self.contract_abi = self.deployed_contract["abi"]
        self.contract = self.w3.eth.contract(address=self.contract_address, abi=self.contract_abi)
    
    async def update_from_hub(self, *args, **kwargs):
        logger.info("~~Updating from Hub~~")
        
        # get CID from smart contract
        cid = self.contract.functions.getRootCID().call()
        print()
        print("CID from smart contract: ", cid)
        print()
        # check to see if a file with that CID exists in the directories folder
        # if it does, no need to update
        if os.path.exists(f"directories/{cid}") and len(cid)>0:
            return {"status": "success", "message": "Already up to date"}

        await naptha.hub.connect()
        un = os.getenv("HUB_USERNAME")
        pw = os.getenv("HUB_PASSWORD")
        await naptha.hub.signin(un, pw)

        servers = await naptha.hub.list_servers()
        nodes = await naptha.hub.list_nodes()
        agents = await naptha.hub.list_agents()
        tools = await naptha.hub.list_tools()
        orchestrators = await naptha.hub.list_orchestrators()
        environments = await naptha.hub.list_environments()
        personas = await naptha.hub.list_personas()
        memories = await naptha.hub.list_memories()
        kbs = await naptha.hub.list_kbs()

        directory = {
            "servers": servers,
            "nodes": nodes,
            "agents": agents,
            "tools": tools,
            "orchestrators": orchestrators,
            "environments": environments,
            "personas": personas,
            "memories": memories,
            "kbs": kbs
        }

        file = io.BytesIO(json.dumps(directory).encode())
        

        create_storage_request = schemas.CreateStorageRequest(
            storage_type="ipfs",
            path="test_xyz",
            file=file
        )

        create_storage_result = await self.storage_provider.execute(create_storage_request)
        cid = create_storage_result.data['data']["ipfs_hash"]
        
        eth_pk = os.getenv("ETH_PK")
        account = self.w3.eth.account.from_key(eth_pk)

        nonce = self.w3.eth.get_transaction_count(account.address)
        tx = self.contract.functions.setRootCID(cid).build_transaction({
            "chainId": int(os.getenv("ETH_CHAIN_ID")),
            "gas": 3000000,
            "from": account.address,
            "nonce": nonce,
            "gasPrice": self.w3.to_wei("10", "gwei") # TODO: estimate gas price
        })
        signed_tx = self.w3.eth.account.sign_transaction(tx, private_key=eth_pk)
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        print("Transaction successful!")

        # save file to directories folder as json
        with open(f"directories/{cid}", "w") as f:
            f.write(json.dumps(directory))

        return {"status": "success", "message": "Successfully updated from Hub"}

    async def get_directory(self, *args, **kwargs):
        logger.info("~~Getting Directory~~")
        # check to see if a file with that CID exists in the directories folder
        # if it does, read the file and use that as directory
        # if it does not, pull from IPFS and save to directories folder
        cid = self.contract.functions.getRootCID().call()
        if os.path.exists(f"directories/{cid}"):
            with open(f"directories/{cid}", "r") as f:
                directory = json.load(f)
        else:
            read_storage_request = schemas.ReadStorageRequest(
                storage_type="ipfs",
                path=cid
            )
            read_storage_result = await self.storage_provider.execute(read_storage_request)
            directory = json.loads(read_storage_result.data["data"])
            with open(f"directories/{cid}", "w") as f:
                f.write(json.dumps(directory))
        return directory

    async def get_servers(self, *args, **kwargs):
        logger.info("~~Getting Servers~~")
        directory = await self.get_directory()
        return {"status": "success", "message": directory["servers"]}

    async def get_nodes(self, *args, **kwargs):
        logger.info("~~Getting Nodes~~")
        directory = await self.get_directory()
        return {"status": "success", "message": directory["nodes"]}

    async def get_agents(self, *args, **kwargs):
        logger.info("~~Getting Agents~~")
        directory = await self.get_directory()
        return {"status": "success", "message": directory["agents"]}

    async def get_tools(self, *args, **kwargs):
        logger.info("~~Getting Tools~~")
        directory = await self.get_directory()
        return {"status": "success", "message": directory["tools"]}

    async def get_orchestrators(self, *args, **kwargs):
        logger.info("~~Getting Orchestrators~~")
        directory = await self.get_directory()
        return {"status": "success", "message": directory["orchestrators"]}

    async def get_environments(self, *args, **kwargs):
        logger.info("~~Getting Environments~~")
        directory = await self.get_directory()
        return {"status": "success", "message": directory["environments"]}

    async def get_personas(self, *args, **kwargs):
        logger.info("~~Getting Personas~~")
        directory = await self.get_directory()
        return {"status": "success", "message": directory["personas"]}

    async def get_memories(self, *args, **kwargs):
        logger.info("~~Getting Memories~~")
        directory = await self.get_directory()
        return {"status": "success", "message": directory["memories"]}

    async def get_kbs(self, *args, **kwargs):
        logger.info("~~Getting KBS~~")
        directory = await self.get_directory()
        return {"status": "success", "message": directory["kbs"]}

    async def test(self, *args, **kwargs):
        logger.info("~~Testing~~")
        
        print()
        print()
        print("Connecting to hub")
        await naptha.hub.connect()
        un = os.getenv("HUB_USERNAME")
        pw = os.getenv("HUB_PASSWORD")
        await naptha.hub.signin(un, pw)
        print(f"Hub Authenticated: {naptha.hub.is_authenticated}")
 
        # ETH stuff
        eth_pk = os.getenv("ETH_PK")
        eth_url = os.getenv("ETH_NODE_URL")
        w3 = Web3(Web3.HTTPProvider(eth_url))
        account = w3.eth.account.from_key(eth_pk)
        print("ETH Account: ", account.address)

        # get address and ABI from ../onchain_registry/deployed-contract.json
        with open("../onchain_registry/deployed-contract.json", "r") as f:
            deployed_contract = json.load(f)

        # ensure that the contract address and ABI are correct
        contract_address = deployed_contract["address"]
        contract_abi = deployed_contract["abi"]

        
        contract = w3.eth.contract(address=contract_address, abi=contract_abi)

        # get the contract owner
        contract_owner = contract.functions.getOwner().call()
        print("Contract owner: ", contract_owner)

        servers = await naptha.hub.list_servers()
        nodes = await naptha.hub.list_nodes()
        agents = await naptha.hub.list_agents()
        tools = await naptha.hub.list_tools()
        orchestrators = await naptha.hub.list_orchestrators()
        environments = await naptha.hub.list_environments()
        personas = await naptha.hub.list_personas()
        memories = await naptha.hub.list_memories()
        kbs = await naptha.hub.list_kbs()

        directory = {
            "servers": servers,
            "nodes": nodes,
            "agents": agents,
            "tools": tools,
            "orchestrators": orchestrators,
            "environments": environments,
            "personas": personas,
            "memories": memories,
            "kbs": kbs
        }
        
        # create file to post from directory (in memory)
        file = io.BytesIO(json.dumps(directory).encode())
        

        create_storage_request = schemas.CreateStorageRequest(
            storage_type="ipfs",
            path="test_xyz",
            file=file
        )

        create_storage_result = await self.storage_provider.execute(create_storage_request)
        cid = create_storage_result.data['data']["ipfs_hash"]

        read_storage_request = schemas.ReadStorageRequest(
            storage_type="ipfs",
            path=cid
        )
        read_storage_result = await self.storage_provider.execute(read_storage_request)

        print("CID: ", cid)
        
        # register CID to smart contract
        nonce = w3.eth.get_transaction_count(account.address)
        tx = contract.functions.setRootCID(cid).build_transaction({
            "chainId": 31337,
            "gas": 3000000,
            "from": account.address,
            "nonce": nonce,
            "gasPrice": w3.to_wei("10", "gwei")
        })

        signed_tx = w3.eth.account.sign_transaction(tx, private_key=eth_pk)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        print("Transaction successful!")
        print("Transaction hash:", tx_receipt.transactionHash.hex())
        print("Block number:", tx_receipt.blockNumber)

        print("Reading CID from smart contract")
        cid = contract.functions.getRootCID().call()
        print("CID from smart contract: ", cid)

        # get CID from smart contract
        return {"status": "success", "message": "Test successful"}
        #return {"status": "success", "message": f"List rows result: {list_storage_result}"}

# TODO: Make it so that the create function is called when the kb/create endpoint is called
async def create(deployment: KBDeployment):
    pass

# Default entrypoint when the module is executed
async def run(module_run: Dict):
    module_run = KBRunInput(**module_run)
    
    module_run.inputs = InputSchema(**module_run.inputs)
    
    onchain_hub_kb = OnchainHubKB(module_run.deployment)
    
    method = getattr(onchain_hub_kb, module_run.inputs.func_name, None)
    
    return await method(module_run.inputs.func_input_data)

if __name__ == "__main__":
    import asyncio
    from naptha_sdk.client.naptha import Naptha
    from naptha_sdk.configs import setup_module_deployment
    import os

    naptha = Naptha()
    deployment = asyncio.run(setup_module_deployment("kb", "onchain_hub_kb/configs/deployment.json", node_url = os.getenv("NODE_URL")))

    inputs_dict = {
        "init": {
            "func_name": "init",
            "func_input_data": None,
        },
        "update_from_hub": {
            "func_name": "update_from_hub",
            "func_input_data": None
        },
        "get_directory": {
            "func_name": "get_directory",
            "func_input_data": None
        },
        "get_servers": {
            "func_name": "get_servers",
            "func_input_data": None
        },
        "get_nodes": {
            "func_name": "get_nodes",
            "func_input_data": None
        },
        "get_agents": {
            "func_name": "get_agents",
            "func_input_data": None
        },
        "get_tools": {
            "func_name": "get_tools",
            "func_input_data": None
        },
        "get_orchestrators": {
            "func_name": "get_orchestrators",
            "func_input_data": None
        },
        "get_environments": {
            "func_name": "get_environments",
            "func_input_data": None
        },
        "get_personas": {
            "func_name": "get_personas",
            "func_input_data": None
        },
        "get_memories": {
            "func_name": "get_memories",
            "func_input_data": None
        },
        "get_kbs": {
            "func_name": "get_kbs",
            "func_input_data": None
        }
    }


    module_run = {
        "inputs": inputs_dict["update_from_hub"],
        "deployment": deployment,
        "consumer_id": naptha.user.id,
        "signature": sign_consumer_id(naptha.user.id, os.getenv("PRIVATE_KEY"))
    }

    response = asyncio.run(run(module_run))

    get_personas_run = {
        "inputs": inputs_dict["get_personas"],
        "deployment": deployment,
        "consumer_id": naptha.user.id,
        "signature": sign_consumer_id(naptha.user.id, os.getenv("PRIVATE_KEY"))
    }

    response = asyncio.run(run(get_personas_run))
    
    get_agents_run = {
        "inputs": inputs_dict["get_agents"],
        "deployment": deployment,
        "consumer_id": naptha.user.id,
        "signature": sign_consumer_id(naptha.user.id, os.getenv("PRIVATE_KEY"))
    }

    response = asyncio.run(run(get_agents_run))

    print("Response: ", response)