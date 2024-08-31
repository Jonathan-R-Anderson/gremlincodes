// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/Counters.sol";
import "@openzeppelin/contracts/token/ERC721/IERC721.sol";  // Import standard ERC721 interface

contract GremlinThread is Ownable {
    using Counters for Counters.Counter;
    Counters.Counter private _threadIdCounter;

    IERC721 public gctnToken;
    string public domain;

    // Structure to store thread details
    struct Thread {
        uint256 id;                  // Unique ID for the thread
        address ethAddress;          // Ethereum address of the thread creator
        string subject;              // Subject of the thread
        string[] tags;               // Tags associated with the thread
        string[] attachments;        // Attachments associated with the thread
        string threadDomain;         // Domain the thread is associated with (renamed from `domain` to `threadDomain` to avoid shadowing)
        bool isBlacklisted;          // Boolean flag to indicate if the thread is blacklisted
    }

    mapping(uint256 => Thread) public threads;         // Mapping from thread ID to Thread structure
    mapping(address => uint256[]) public userThreads;  // Mapping from user address to array of thread IDs
    mapping(string => uint256[]) public threadsByTag;  // Mapping from tag name to array of thread IDs

    event ThreadCreated(
        uint256 id,
        address ethAddress,
        string subject,
        string[] tags,
        string[] attachments,
        string threadDomain
    );

    event ThreadBlacklisted(uint256 threadId);
    event Debug(string message);  // Debug event to log messages
    event ThreadCounterUpdated(uint256 newCount);  // Event to log the thread counter

    constructor(address tokenAddress, string memory _domain) {
        gctnToken = IERC721(tokenAddress);
        domain = _domain;
        emit Debug("Contract initialized");
    }

    modifier onlyTokenHolder(uint256 tokenAmount) {
        require(gctnToken.balanceOf(msg.sender) >= tokenAmount, "Insufficient GCTN tokens");
        emit Debug("Token holder validated");
        _;
    }

    // Function to create a new thread
    function createThread(
        string memory subject,
        string[] memory tags,
        string[] memory attachments
    ) public onlyTokenHolder(1) {
        emit Debug("createThread called");
        _createThread(subject, tags, attachments, msg.sender);
    }

    // Internal function to handle thread creation
    function _createThread(
        string memory subject,
        string[] memory tags,
        string[] memory attachments,
        address ethAddress
    ) internal {
        _threadIdCounter.increment();
        uint256 newThreadId = _threadIdCounter.current();
        emit ThreadCounterUpdated(newThreadId);  // Log the new thread ID

        threads[newThreadId] = Thread({
            id: newThreadId,
            ethAddress: ethAddress,
            subject: subject,
            tags: tags,
            attachments: attachments,
            threadDomain: domain,  // Use the contract's domain
            isBlacklisted: false
        });

        userThreads[ethAddress].push(newThreadId);

        for (uint256 i = 0; i < tags.length; i++) {
            threadsByTag[tags[i]].push(newThreadId);
        }

        emit ThreadCreated(newThreadId, ethAddress, subject, tags, attachments, domain);
        emit Debug("Thread created successfully");
    }

    function getThreadCount() public view returns (uint256) {
        uint256 count = _threadIdCounter.current();
        emit Debug("getThreadCount called");
        emit ThreadCounterUpdated(count);  // Log the current thread count
        return count;
    }

    // Function to blacklist a thread
    function blacklistThread(uint256 threadId) external onlyOwner {
        Thread storage thread = threads[threadId];
        require(thread.id != 0, "Thread does not exist");
        thread.isBlacklisted = true;
        emit ThreadBlacklisted(threadId);
        emit Debug("Thread blacklisted");
    }

    // Function to get thread information
    function getThreadInfo(uint256 threadId) external view returns (
        uint256 id,
        address ethAddress,
        string memory subject,
        string[] memory tags,
        string[] memory attachments,
        string memory threadDomain,
        bool isBlacklisted
    ) {
        Thread storage thread = threads[threadId];
        require(thread.id != 0, "Thread does not exist");
        emit Debug("getThreadInfo called");
        return (
            thread.id,
            thread.ethAddress,
            thread.subject,
            thread.tags,
            thread.attachments,
            thread.threadDomain,
            thread.isBlacklisted
        );
    }
}
