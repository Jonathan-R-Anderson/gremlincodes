// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "./GremlinThread.sol";
import "./GremlinReply.sol";

contract GremlinAdmin {
    
    address public owner;
    GremlinThread public gremlinThread;
    GremlinReply public gremlinReply;

    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner can perform this action");
        _;
    }

    constructor(address _gremlinThreadAddress, address _gremlinReplyAddress) {
        owner = msg.sender;
        gremlinThread = GremlinThread(_gremlinThreadAddress);
        gremlinReply = GremlinReply(_gremlinReplyAddress);
    }

    // Ban a user globally from both threads and replies
    function banUser(address _user) public onlyOwner {
        gremlinThread.banAddress(_user);
        gremlinReply.banAddress(_user);
    }

    // Unban a user globally
    function unbanUser(address _user) public onlyOwner {
        gremlinThread.unbanAddress(_user);
        gremlinReply.unbanAddress(_user);
    }

    // Blacklist a thread globally
    function blacklistThread(uint256 _threadId) public onlyOwner {
        gremlinThread.blacklistThread(_threadId);
    }

    // Whitelist a thread globally
    function whitelistThread(uint256 _threadId) public onlyOwner {
        gremlinThread.whitelistThread(_threadId);
    }

    // Soft delete a thread globally
    function deleteThread(uint256 _threadId) public onlyOwner {
        gremlinThread.deleteThread(_threadId);  // Soft delete thread
    }

    // Blacklist a reply globally
    function blacklistReply(uint256 _replyId) public onlyOwner {
        gremlinReply.blacklistReply(_replyId);
    }

    // Whitelist a reply globally
    function whitelistReply(uint256 _replyId) public onlyOwner {
        gremlinReply.whitelistReply(_replyId);
    }

    // Delete a reply globally
    function deleteReply(uint256 _replyId) public onlyOwner {
        gremlinReply.deleteReply(_replyId);
    }
}
