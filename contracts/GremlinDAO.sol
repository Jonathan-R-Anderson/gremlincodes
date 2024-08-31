// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721Enumerable.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import "@openzeppelin/contracts/utils/Counters.sol";

contract GremlinDAO is ERC721Enumerable, ERC721URIStorage, Ownable {
    using Counters for Counters.Counter;

    Counters.Counter private _tokenIdCounter;
    string public domain;

    // Address of the SysAdmin who will manage the DAO
    address public sysAdmin;
    // Reserve where tokens will be kept and managed by the DAO
    uint256 public reserve;
    // Maximum supply of tokens allowed in circulation
    uint256 public maxSupply = 1000000; // Max supply set to 1,000,000
    // Initial reserve supply
    uint256 public initialReserve = 10000; // Reserve set to 10,000

    // DAO parameters
    bool public voteActive;
    uint256 public totalVoteOptions;
    uint256 public totalVotesCast;
    uint256 public totalWeightedVotes;

    struct VoteOption {
        string description;
        uint256 voteWeight;
    }

    struct TagInfo {
        string name;
        uint256 usageCount;
    }

    mapping(uint256 => VoteOption) public voteOptions;
    mapping(string => bool) public existingTags;
    mapping(string => uint256) public tagUsageCount;
    TagInfo[] public allTags;

    // Contracts for thread and post management
    address public threadContract;
    address public postContract;

    uint256 public tagCreationCost = 10;
    uint256 public tagCreationInterval = 1 weeks;
    uint256 public lastTagCreationTime;

    event TagCreated(string tag, uint256 cost);
    event VoteCancelled();
    event TipAwarded(address recipient, uint256 amount);
    event MagnetNFTMinted(address to, uint256 tokenId, string magnetURL);

    constructor(address _sysAdmin) ERC721("Gremlin.Codes Token", "GCTN") {
        sysAdmin = _sysAdmin;
        reserve = initialReserve; // Set the initial reserve
    }

    modifier onlySysAdmin() {
        require(msg.sender == sysAdmin, "Not authorized");
        _;
    }

    modifier onlyGCTNHolder(uint256 tokenAmount) {
        require(balanceOf(msg.sender) >= tokenAmount, "Insufficient GCTN tokens");
        _;
    }

    // SysAdmin functions
    function setSysAdmin(address newSysAdmin) external onlyOwner {
        sysAdmin = newSysAdmin;
    }

    function setMaxSupply(uint256 newMaxSupply) external onlySysAdmin {
        require(newMaxSupply >= totalSupply(), "New max supply must be greater than or equal to current supply");
        maxSupply = newMaxSupply;
    }

    function setReserve(uint256 newReserve) external onlySysAdmin {
        require(newReserve <= maxSupply - totalSupply(), "Reserve cannot exceed available supply");
        reserve = newReserve;
    }

    function setContracts(address _threadContract, address _postContract) external onlySysAdmin {
        threadContract = _threadContract;
        postContract = _postContract;
    }

    function setDomain(string memory _domain) external onlySysAdmin {
        domain = _domain;
    }

    function createTag(string memory tag) public onlyGCTNHolder(tagCreationCost) {
        require(!existingTags[tag], "Tag already exists");
        _adjustTagCreationCost();
        existingTags[tag] = true;
        tagUsageCount[tag] = 1;
        allTags.push(TagInfo(tag, 1));
        emit TagCreated(tag, tagCreationCost);
    }

    function createTagBySysAdmin(string memory tag) public onlySysAdmin {
        require(!existingTags[tag], "Tag already exists");
        _adjustTagCreationCost();
        existingTags[tag] = true;
        tagUsageCount[tag] = 1;
        allTags.push(TagInfo(tag, 1));
        emit TagCreated(tag, tagCreationCost);
    }

    function incrementTagUsage(string memory tag) public onlySysAdmin {
        require(existingTags[tag], "Tag does not exist");
        tagUsageCount[tag] += 1;
        for (uint256 i = 0; i < allTags.length; i++) {
            if (keccak256(bytes(allTags[i].name)) == keccak256(bytes(tag))) {
                allTags[i].usageCount = tagUsageCount[tag];
                break;
            }
        }
    }

    function getAllTags() public view returns (TagInfo[] memory) {
        return allTags;
    }

    // Function to get the usage count of a specific tag
    function getTagUsage(string memory tag) public view returns (uint256) {
        require(existingTags[tag], "Tag does not exist");
        return tagUsageCount[tag];
    }

    function _adjustTagCreationCost() internal {
        if (block.timestamp - lastTagCreationTime < tagCreationInterval) {
            tagCreationCost += 1;
        } else {
            tagCreationCost = tagCreationCost > 1 ? tagCreationCost - 1 : 1;
        }
        lastTagCreationTime = block.timestamp;
    }

    function cancelVote() public onlySysAdmin {
        voteActive = false;
        totalVotesCast = 0;
        totalWeightedVotes = 0;

        for (uint256 i = 0; i < totalVoteOptions; i++) {
            voteOptions[i].voteWeight = 0;
        }

        emit VoteCancelled();
    }

    function tipToken(address recipient, uint256 timeOnPage, uint256 avgTimeOnPage) external {
        uint256 multiplier = 1;
        if (timeOnPage >= avgTimeOnPage * 2) {
            multiplier = 2;
        } else if (timeOnPage >= avgTimeOnPage * 3) {
            multiplier = 3;
        }

        uint256 tokensToTip = 1 * multiplier;
        mintToken(recipient);

        emit TipAwarded(recipient, tokensToTip);

        // Regulate the token supply to ensure there are not too many tokens in circulation
        regulateTokenSupply();
    }

    function regulateTokenSupply() internal {
        uint256 circulatingSupply = totalSupply();
        if (circulatingSupply > maxSupply) {
            regulateSupply();
        }
    }

    function mintToken(address to) internal onlySysAdmin {
        require(_tokenIdCounter.current() < maxSupply, "Max supply reached");
        _tokenIdCounter.increment();
        uint256 newTokenId = _tokenIdCounter.current();
        _mint(to, newTokenId);
    }

    function burnToken(uint256 tokenId) public onlySysAdmin {
        require(_exists(tokenId), "Token does not exist");
        _burn(tokenId);
        reserve -= 1;
    }

    function regulateSupply() internal {
        uint256 circulatingSupply = totalSupply() - reserve;
        if (circulatingSupply > maxSupply) {
            burnExcessTokens();
        }
    }

    function burnExcessTokens() internal {
        uint256 tokensToBurn = reserve;
        for (uint256 i = 0; i < tokensToBurn; i++) {
            uint256 tokenId = tokenOfOwnerByIndex(sysAdmin, i);
            burnToken(tokenId);
        }
    }

    function submitPost(uint256 threadId) external onlyGCTNHolder(1) {
        uint256 tokenId = tokenOfOwnerByIndex(msg.sender, 0);
        safeTransferFrom(msg.sender, address(this), tokenId);
    }

    // Function to mint NFTs for magnet URLs
    function mintMagnetNFT(address to, string memory magnetURL) public onlySysAdmin {
        require(_tokenIdCounter.current() < maxSupply, "Max supply reached");
        _tokenIdCounter.increment();
        uint256 newTokenId = _tokenIdCounter.current();
        _mint(to, newTokenId);
        
        // Store the magnet URL as the token URI
        _setTokenURI(newTokenId, magnetURL);
        
        emit MagnetNFTMinted(to, newTokenId, magnetURL);
    }

    // Override _beforeTokenTransfer to resolve conflict
    function _beforeTokenTransfer(address from, address to, uint256 tokenId) internal override(ERC721, ERC721Enumerable) {
        super._beforeTokenTransfer(from, to, tokenId);
    }

    // Override _burn to ensure token URI is deleted as well
    function _burn(uint256 tokenId) internal override(ERC721, ERC721URIStorage) {
        super._burn(tokenId);
    }

    // Override tokenURI to use ERC721URIStorage implementation
    function tokenURI(uint256 tokenId) public view override(ERC721, ERC721URIStorage) returns (string memory) {
        return super.tokenURI(tokenId);
    }

    // Override supportsInterface to include ERC721Enumerable
    function supportsInterface(bytes4 interfaceId) public view override(ERC721, ERC721Enumerable) returns (bool) {
        return super.supportsInterface(interfaceId);
    }
}
