// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

contract Poster {
    struct PosterInfo {
        uint256 postCount;
        uint256 threadCount;
        uint256 nftCount;
        string profilePicture;
        mapping(string => uint256) tagsUsed;
        string[] nftMagnetUrls;
        uint256 gctnTokenBalance;
    }

    IERC20 public gctnToken;
    string public domain;

    mapping(address => PosterInfo) public posters;

    constructor(address _gctnTokenAddress) {
        gctnToken = IERC20(_gctnTokenAddress);
    }

    function setDomain(string memory _domain) external {
        domain = _domain;
    }

    function incrementPostCount(address poster) external {
        posters[poster].postCount += 1;
    }

    function incrementThreadCount(address poster) external {
        posters[poster].threadCount += 1;
    }

    function updateTokenBalance(address poster) external {
        uint256 balance = gctnToken.balanceOf(poster);
        posters[poster].gctnTokenBalance = balance;
    }

    function addNftMagnetUrl(address poster, string memory magnetUrl) external {
        posters[poster].nftMagnetUrls.push(magnetUrl);
        posters[poster].nftCount += 1;
    }

    function setProfilePicture(address poster, string memory magnetUrl) external {
        posters[poster].profilePicture = magnetUrl;
    }

    function incrementTagUsage(address poster, string memory tag) external {
        posters[poster].tagsUsed[tag] += 1;
    }

    function getPosterInfo(address poster) external view returns (
        uint256 postCount,
        uint256 threadCount,
        uint256 nftCount,
        string memory profilePicture,
        uint256 gctnTokenBalance
    ) {
        PosterInfo storage info = posters[poster];
        return (
            info.postCount,
            info.threadCount,
            info.nftCount,
            info.profilePicture,
            info.gctnTokenBalance
        );
    }

    function getNftMagnetUrls(address poster) external view returns (string[] memory) {
        return posters[poster].nftMagnetUrls;
    }

    function getTagUsage(address poster, string memory tag) external view returns (uint256) {
        return posters[poster].tagsUsed[tag];
    }

    function getContributionScore(address poster) external view returns (uint256) {
        uint256 posterBalance = posters[poster].gctnTokenBalance;
        uint256 totalSupply = gctnToken.totalSupply();
        
        require(totalSupply > 0, "Total supply must be greater than zero");
        
        return (posterBalance * 1e18) / totalSupply;
    }

    function getPostCount(address poster) external view returns (uint256) {
        return posters[poster].postCount;
    }

    function getThreadCount(address poster) external view returns (uint256) {
        return posters[poster].threadCount;
    }

    function getProfilePicture(address poster) external view returns (string memory) {
        return posters[poster].profilePicture;
    }

    function setPostCount(address poster, uint256 newCount) external {
        posters[poster].postCount = newCount;
    }

    function setThreadCount(address poster, uint256 newCount) external {
        posters[poster].threadCount = newCount;
    }

    function setProfilePictureDirectly(address poster, string memory newPicture) external {
        posters[poster].profilePicture = newPicture;
    }

    function getAllNftMagnetUrls(address poster) external view returns (string memory) {
        PosterInfo storage info = posters[poster];
        string memory allNftUrls = "";
        
        for (uint256 i = 0; i < info.nftMagnetUrls.length; i++) {
            allNftUrls = string(abi.encodePacked(allNftUrls, info.nftMagnetUrls[i], " "));
        }
        
        return allNftUrls;
    }
}
