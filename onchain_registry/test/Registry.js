const {
    time,
    loadFixture,
  } = require("@nomicfoundation/hardhat-toolbox/network-helpers");
const { anyValue } = require("@nomicfoundation/hardhat-chai-matchers/withArgs");
const { expect } = require("chai");
const fetch = require('node-fetch');
const FormData = require('form-data');
const IPFS_API_URL = 'http://127.0.0.1:5001/api/v0';

    describe("Registry", function () {
      async function deployRegistryFixture() {
        const Registry = await ethers.getContractFactory("Registry");
        const registry = await Registry.deploy();
    
        return { registry };
      }

      async function uploadAndPin(jsonData) {
          try {
              const formData = new FormData();
              const jsonBuffer = Buffer.from(JSON.stringify(jsonData));
              formData.append('file', jsonBuffer, { filename: 'data.json', contentType: 'application/json' });
              
              const response = await fetch(`${IPFS_API_URL}/add`, {
                  method: 'POST',
                  body: formData
              });
              
              if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
              
              const data = await response.json();
              console.log(`Uploaded JSON and received CID: ${data.Hash}`);
              return data.Hash;
          } catch (error) {
              console.error(`Failed to upload JSON: ${error.message}`);
              return null;
          }
      }

      async function getFile(cid) {
          try {
              const response = await fetch(`${IPFS_API_URL}/cat?arg=${cid}`, {
                  method: 'POST'
              });
              
              if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
              
              const jsonData = await response.json();
              console.log(`Retrieved JSON data:`, jsonData);
              return jsonData;
          } catch (error) {
              console.error(`Failed to retrieve JSON: ${error.message}`);
              return null;
          }
      }
    
      describe("Deployment", function () {
        it("Should deploy the Registry", async function () {
          const { registry } = await loadFixture(deployRegistryFixture);
    
          expect(registry.address).to.not.equal(0);
        });
      });
    
      describe("register", function () {
        it("store a string to IPFS and register the CID with the smart contract", async function () {
            const { registry } = await loadFixture(deployRegistryFixture);
            const test_object = { "x": "this is a test", "y": 1234 };
            const cid = await uploadAndPin(test_object);

            console.log(cid);

            let tx = await registry.setRootCID(cid);

            
            let tx_receipt = await tx.wait();
            

            // get event RootCIDSet(string rootCID);
            events = tx_receipt.logs;
            console.log(events[0].args[0]);

            const rootCID = await registry.getRootCID();

            expect(rootCID).to.equal(cid);
        });
      });
    })