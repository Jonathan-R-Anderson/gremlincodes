// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/Counters.sol";
import "@openzeppelin/contracts/token/ERC721/IERC721.sol";  // Import standard ERC721 interface
import "./GremlinThread.sol";  // Import the GremlinThread contract

contract GremlinPost is Ownable {
    using Counters for Counters.Counter;
    
    // Counter to track the post IDs
    Counters.Counter private _postIdCounter;

    // Instance of the GremlinThread contract
    GremlinThread public threadContract;
    
    // Domain associated with the GremlinPost contract
    string public domain;
    
    // Interface for the GCTNToken contract
    IERC721 public gctnToken;

    struct Post {
        uint256 id;             // Unique ID for the post
        uint256 threadId;       // ID of the thread the post belongs to
        string name;            // Name of the post author
        string email;           // Email of the post author
        address ethAddress;     // Ethereum address of the post author
        bytes32 tripCode;       // Trip code for author verification
        string magnetURL;       // Magnet URL associated with the post
        string postDomain;      // Domain the post is associated with
    }

    mapping(uint256 => Post) public posts;
    
    mapping(address => uint256[]) public userPosts;

    event PostCreated(
        uint256 id,
        uint256 threadId,
        string name,
        string email,
        address ethAddress,
        bytes32 tripCode,
        string magnetURL,
        string postDomain
    );

    constructor(address threadContractAddress, string memory _domain, address tokenAddress) {
        threadContract = GremlinThread(threadContractAddress);
        domain = _domain;
        gctnToken = IERC721(tokenAddress);
    }

    modifier onlyGCTNHolder(uint256 tokenAmount) {
        require(gctnToken.balanceOf(msg.sender) >= tokenAmount, "Insufficient GCTN tokens");
        _;
    }

    modifier onlySysAdmin() {
        require(msg.sender == owner(), "Not authorized");
        _;
    }

    function createPost(
        uint256 threadId,
        string memory name,
        string memory email,
        bytes32 tripCode,
        string memory magnetURL,
        string memory postDomain
    ) public onlyGCTNHolder(1) {
        _createPost(threadId, name, email, tripCode, magnetURL, postDomain, msg.sender);
    }

    function createPostBySysAdmin(
        uint256 threadId,
        string memory name,
        string memory email,
        bytes32 tripCode,
        string memory magnetURL,
        string memory postDomain
    ) public onlySysAdmin {
        _createPost(threadId, name, email, tripCode, magnetURL, postDomain, owner());
    }

    function _createPost(
        uint256 threadId,
        string memory name,
        string memory email,
        bytes32 tripCode,
        string memory magnetURL,
        string memory postDomain,
        address ethAddress
    ) internal {
        // Adjust this to match the number of returned values from getThreadInfo
        (uint256 threadIdRetrieved, address threadOwnerAddress, string memory subject, string[] memory tags, string[] memory attachments, string memory threadDomain, bool isBlacklisted) = threadContract.getThreadInfo(threadId);

        require(!isBlacklisted, "Thread is blacklisted");

        _postIdCounter.increment();
        uint256 newPostId = _postIdCounter.current();

        posts[newPostId] = Post({
            id: newPostId,
            threadId: threadId,
            name: name,
            email: email,
            ethAddress: ethAddress,
            tripCode: tripCode,
            magnetURL: magnetURL,
            postDomain: postDomain
        });

        userPosts[ethAddress].push(newPostId);

        emit PostCreated(newPostId, threadId, name, email, ethAddress, tripCode, magnetURL, postDomain);
    }
}
