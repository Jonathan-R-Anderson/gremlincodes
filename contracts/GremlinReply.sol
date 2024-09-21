// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract GremlinReply {

    struct Reply {
        uint256 id;
        string content;
        string email;
        string magnetUrl;
        uint256 parentId;  // Points to either a thread or another reply
        address sender;
        uint256 timestamp;
        bool whitelisted;
        bool blacklisted;
    }

    uint256 public replyCount = 0;
    mapping(uint256 => Reply) public replies;
    mapping(address => bool) public bannedAddresses;

    address public admin;

    modifier onlyAdmin() {
        require(msg.sender == admin, "Only admin can perform this action");
        _;
    }

    modifier notBanned() {
        require(!bannedAddresses[msg.sender], "Sender is banned");
        _;
    }

    constructor() {
        admin = msg.sender;
    }

    // Create a new reply
    function createReply(
        string memory _content,
        string memory _email,
        string memory _magnetUrl,
        uint256 _parentId
    ) public notBanned {
        replyCount++;
        replies[replyCount] = Reply(
            replyCount,
            _content,
            _email,
            _magnetUrl,
            _parentId,
            msg.sender,
            block.timestamp,
            true,  // Whitelisted by default
            false  // Not blacklisted by default
        );
    }

    // Blacklist a reply (by admin)
    function blacklistReply(uint256 _replyId) public onlyAdmin {
        replies[_replyId].blacklisted = true;
    }

    // Whitelist a reply (by admin)
    function whitelistReply(uint256 _replyId) public onlyAdmin {
        replies[_replyId].whitelisted = true;
    }

    // Delete a reply (by admin)
    function deleteReply(uint256 _replyId) public onlyAdmin {
        delete replies[_replyId];
    }

    // Ban an address (by admin)
    function banAddress(address _addr) public onlyAdmin {
        bannedAddresses[_addr] = true;
    }

    // Unban an address (by admin)
    function unbanAddress(address _addr) public onlyAdmin {
        bannedAddresses[_addr] = false;
    }

    // Get all replies
    function getAllReplies() public view returns (Reply[] memory) {
        Reply[] memory allReplies = new Reply[](replyCount);
        for (uint256 i = 1; i <= replyCount; i++) {
            allReplies[i - 1] = replies[i];
        }
        return allReplies;
    }
}
