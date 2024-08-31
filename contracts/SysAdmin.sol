// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/access/Ownable.sol";
import "./GremlinThread.sol";
import "./GremlinPost.sol";
import "./Poster.sol";
import "./GremlinDAO.sol";

contract SysAdmin is Ownable {
    string public domain;
    GremlinThread public threadContract;
    GremlinPost public postContract;
    Poster public posterContract;
    GremlinDAO public daoContract;

    mapping(address => bool) public moderators;

    // Blacklist/Whitelist mappings
    mapping(uint256 => bool) public blacklistedThreads;
    mapping(uint256 => bool) public blacklistedPosts;
    mapping(string => bool) public blacklistedTags;
    mapping(address => bool) public blacklistedAddresses;
    mapping(string => bool) public blacklistedDomains;
    mapping(string => bool) public blacklistedIPs;

    event ThreadBlacklisted(uint256 threadId);
    event ThreadWhitelisted(uint256 threadId);
    event PostBlacklisted(uint256 postId);
    event PostWhitelisted(uint256 postId);
    event ModeratorAdded(address moderator);
    event ModeratorRemoved(address moderator);
    event VoteCancelled();

    modifier onlyModerator() {
        require(moderators[msg.sender] || msg.sender == owner(), "Not authorized");
        _;
    }

    constructor(string memory _domain) {
        domain = _domain;
    }

    function addModerator(address moderator) public onlyOwner {
        moderators[moderator] = true;
        emit ModeratorAdded(moderator);
    }

    function removeModerator(address moderator) public onlyOwner {
        moderators[moderator] = false;
        emit ModeratorRemoved(moderator);
    }

    function blacklistThread(uint256 threadId) public onlyModerator {
        blacklistedThreads[threadId] = true;
        emit ThreadBlacklisted(threadId);
    }

    function whitelistThread(uint256 threadId) public onlyModerator {
        blacklistedThreads[threadId] = false;
        emit ThreadWhitelisted(threadId);
    }

    function blacklistPost(uint256 postId) public onlyModerator {
        blacklistedPosts[postId] = true;
        emit PostBlacklisted(postId);
    }

    function whitelistPost(uint256 postId) public onlyModerator {
        blacklistedPosts[postId] = false;
        emit PostWhitelisted(postId);
    }

    function blacklistTag(string memory tag) public onlyModerator {
        blacklistedTags[tag] = true;
    }

    function whitelistTag(string memory tag) public onlyModerator {
        blacklistedTags[tag] = false;
    }

    function blacklistAddress(address userAddress) public onlyModerator {
        blacklistedAddresses[userAddress] = true;
    }

    function whitelistAddress(address userAddress) public onlyModerator {
        blacklistedAddresses[userAddress] = false;
    }

    function blacklistDomain(string memory targetDomain) public onlyModerator {
        blacklistedDomains[targetDomain] = true;
    }

    function whitelistDomain(string memory targetDomain) public onlyModerator {
        blacklistedDomains[targetDomain] = false;
    }

    function blacklistIP(string memory ip) public onlyModerator {
        blacklistedIPs[ip] = true;
    }

    function whitelistIP(string memory ip) public onlyModerator {
        blacklistedIPs[ip] = false;
    }

    function cancelVote() public onlyOwner {
        daoContract.cancelVote();
        emit VoteCancelled();
    }
}
