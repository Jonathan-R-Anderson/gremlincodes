// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract GremlinProfile {
    struct Profile {
        string name;
        string bio;
        string css;          // Custom CSS for the user's page
        string html;         // Custom HTML for the user's page
        address owner;
        string videoStreamUrl;  // The latest video stream URL (magnet or any other type)
    }
    
    mapping(address => Profile) public profiles;

    event ProfileCreated(address indexed user, string name);
    event ProfileUpdated(address indexed user, string field);
    event StreamUrlUpdated(address indexed user, string videoStreamUrl);
    
    // Create a new profile for the user
    function createProfile(string memory name, string memory bio) public {
        require(profiles[msg.sender].owner == address(0), "Profile already exists.");
        
        profiles[msg.sender] = Profile({
            name: name,
            bio: bio,
            css: "",
            html: "",
            owner: msg.sender,
            videoStreamUrl: ""
        });
        
        emit ProfileCreated(msg.sender, name);
    }
    
    // Update the user's profile CSS
    function updateProfileCSS(string memory css) public {
        require(profiles[msg.sender].owner == msg.sender, "Not the owner of this profile.");
        profiles[msg.sender].css = css;
        emit ProfileUpdated(msg.sender, "css");
    }
    
    // Update the user's profile HTML
    function updateProfileHTML(string memory html) public {
        require(profiles[msg.sender].owner == msg.sender, "Not the owner of this profile.");
        profiles[msg.sender].html = html;
        emit ProfileUpdated(msg.sender, "html");
    }
    
    // Update the user's video stream URL (replaces any previous URL)
    function updateStreamUrl(string memory videoStreamUrl) public {
        require(profiles[msg.sender].owner != address(0), "Profile does not exist.");
        profiles[msg.sender].videoStreamUrl = videoStreamUrl;
        emit StreamUrlUpdated(msg.sender, videoStreamUrl);
    }

    // Get the user's video stream URL
    function getStreamUrl(address user) public view returns (string memory) {
        return profiles[user].videoStreamUrl;
    }

    // Get the user's profile (including CSS, HTML, and bio)
    function getProfile(address user) public view returns (string memory, string memory, string memory, string memory, string memory) {
        Profile storage profile = profiles[user];
        return (profile.name, profile.bio, profile.css, profile.html, profile.videoStreamUrl);
    }
}
