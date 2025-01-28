// hardhat.config.js
require("@nomicfoundation/hardhat-toolbox");

module.exports = {
  solidity: "0.8.19",
  networks: {
    localhost: {
      url: "http://127.0.0.1:8545",
      chainId: 31337,
    }
  }
};

// scripts/deploy.js
async function main() {
  const Registry = await ethers.getContractFactory("Registry");
  console.log("Deploying Registry...");
  const registry = await Registry.deploy();
  await registry.waitForDeployment();
  const address = await registry.getAddress();
  console.log("Registry deployed to:", address);
  
  // Save the contract address and ABI to a file for other apps to use
  const fs = require("fs");
  // abi is in artifacts/contracts/Registry.sol/Registry.json
  // read the file and parse the JSON
  const registry_abi_json = fs.readFileSync('./artifacts/contracts/registry.sol/Registry.json')
  const registry_abi = JSON.parse(registry_abi_json)

  console.log(Registry.interface)
  const contractData = {
    address: address,
    abi: registry_abi.abi,
  };
  
  fs.writeFileSync(
    './deployed-contract.json',
    JSON.stringify(contractData, null, 2)
  );
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });