// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract GremlinThread {
    
    struct Thread {
        uint256 id;
        string name;
        string subject;
        string email;
        string magnetUrl;
        string[] tags;
        string content;
        uint256 parentThreadId;
        address sender;
        uint256 timestamp;
        bool whitelisted;
        bool blacklisted;
        bool deleted;  // Added field to mark if the thread is deleted
    }

    uint256 public threadCount = 0;
    mapping(uint256 => Thread) public threads;
    mapping(address => bool) public bannedAddresses;

    // Admin address
    address public admin;

    // Events
    event ThreadCreated(uint256 id, uint256 parentThreadId, string subject, string email);
    event ThreadWhitelisted(uint256 id);
    event ThreadBlacklisted(uint256 id);
    event ThreadDeleted(uint256 id);  // Event for thread deletion

    // Modifier to ensure the sender is not banned
    modifier notBanned() {
        require(!bannedAddresses[msg.sender], "Sender is banned");
        _;
    }

    // Modifier to restrict actions to admin only
    modifier onlyAdmin() {
        require(msg.sender == admin, "Only admin can perform this action");
        _;
    }

    // Constructor to set the contract admin
    constructor() {
        admin = msg.sender;  // Contract deployer becomes the admin
    }

    // Create a new thread or a reply (if parentThreadId != 0, it's a reply)
    function createThread(
        string memory _name,
        string memory _subject,
        string memory _email,
        string memory _magnetUrl,
        string[] memory _tags,
        string memory _content,
        uint256 _parentThreadId
    ) public notBanned {
        threadCount++;

        threads[threadCount] = Thread(
            threadCount,
            _name,
            _subject,
            _email,
            _magnetUrl,
            _tags,
            _content,
            _parentThreadId,
            msg.sender,
            block.timestamp,
            true,  // Whitelisted by default
            false, // Not blacklisted by default
            false  // Not deleted by default
        );

        emit ThreadCreated(threadCount, _parentThreadId, _subject, _email);
    }

    // Fetch a thread by its ID, returns the thread only if it is not deleted
    function getThread(uint256 _threadId) public view returns (Thread memory) {
        require(!threads[_threadId].deleted, "Thread has been deleted");
        return threads[_threadId];
    }

    // Fetch all threads (this can be gas expensive, consider adding pagination in future)
    function getAllThreads() public view returns (Thread[] memory) {
        Thread[] memory allThreads = new Thread[](threadCount);
        uint256 index = 0;
        for (uint256 i = 1; i <= threadCount; i++) {
            if (!threads[i].deleted) {
                allThreads[index] = threads[i];
                index++;
            }
        }
        return allThreads;
    }

    // Whitelist a thread (by admin)
    function whitelistThread(uint256 _threadId) public onlyAdmin {
        threads[_threadId].whitelisted = true;
        emit ThreadWhitelisted(_threadId);
    }

    // Blacklist a thread (by admin)
    function blacklistThread(uint256 _threadId) public onlyAdmin {
        threads[_threadId].blacklisted = true;
        emit ThreadBlacklisted(_threadId);
    }

    // Soft delete a thread (by admin)
    function deleteThread(uint256 _threadId) public onlyAdmin {
        threads[_threadId].deleted = true;
        emit ThreadDeleted(_threadId);
    }

    // Ban an address (by admin)
    function banAddress(address _addr) public onlyAdmin {
        bannedAddresses[_addr] = true;
    }

    // Unban an address (by admin)
    function unbanAddress(address _addr) public onlyAdmin {
        bannedAddresses[_addr] = false;
    }

    // Transfer admin role
    function transferAdmin(address newAdmin) public onlyAdmin {
        require(newAdmin != address(0), "New admin cannot be the zero address");
        admin = newAdmin;
    }
}
