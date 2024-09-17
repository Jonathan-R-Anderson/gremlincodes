// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "./GremlinThread.sol";

contract GremlinAdmin {
    
    address public owner;
    GremlinThread public gremlinThread;

    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner can perform this action");
        _;
    }

    constructor(address _gremlinThreadAddress) {
        owner = msg.sender;
        gremlinThread = GremlinThread(_gremlinThreadAddress);
    }

    // Ban a user globally
    function banUser(address _user) public onlyOwner {
        gremlinThread.banAddress(_user);
    }

    // Unban a user globally
    function unbanUser(address _user) public onlyOwner {
        gremlinThread.unbanAddress(_user);
    }

    // Blacklist a thread globally
    function blacklistThread(uint256 _threadId) public onlyOwner {
        gremlinThread.blacklistThread(_threadId);
    }

    // Whitelist a thread globally
    function whitelistThread(uint256 _threadId) public onlyOwner {
        gremlinThread.whitelistThread(_threadId);
    }
}
