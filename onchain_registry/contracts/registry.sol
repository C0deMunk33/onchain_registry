// SPDX-License-Identifier: MIT
pragma solidity ^0.8.27;

contract Registry {
    address public owner;
    string public rootCID;

    constructor() {
        owner = msg.sender;
    }

    function changeOwner(address _newOwner) public {
        require(msg.sender == owner, "You aren't the owner");
        owner = _newOwner;
    }

    function getOwner() public view returns (address) {
        return owner;
    }

    function setRootCID(string memory _rootCID) public {
        require(msg.sender == owner, "You aren't the owner");
        rootCID = _rootCID;
        emit RootCIDSet(_rootCID);
    }

    function getRootCID() public view returns (string memory) {
        return rootCID;
    }

    event RootCIDSet(string rootCID);
}