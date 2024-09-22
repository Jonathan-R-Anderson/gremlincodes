// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract GremlinProfile {
    struct Profile {
        string name;
        string bio;
        string css;       // Custom CSS for the user's page
        string html;      // Custom HTML for the user's page
        address owner;
        VideoStream[] streams;  // Array to store the user's past streams
    }
    
    struct VideoStream {
        string magnetUrl;
        uint256 timestamp;  // Timestamp of when the stream was recorded
    }
    
    mapping(address => Profile) public profiles;

    event ProfileCreated(address indexed user, string name);
    event ProfileUpdated(address indexed user, string field);
    event StreamStarted(address indexed user, string magnetUrl, uint256 timestamp);
    
    // Create a new profile for the user
    function createProfile(string memory name, string memory bio) public {
        require(profiles[msg.sender].owner == address(0), "Profile already exists.");
        
        // Initialize the profile without explicitly setting an empty array for streams (Solidity does this automatically)
        profiles[msg.sender] = Profile({
            name: name,
            bio: bio,
            css: "",
            html: "",
            owner: msg.sender,
            streams: new VideoStream  // No need for this, it will be an empty array by default
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
    
    // Start a new stream and save the magnet URL to the user's profile
    function startStream(string memory magnetUrl) public {
        require(profiles[msg.sender].owner == msg.sender, "Profile does not exist.");
        profiles[msg.sender].streams.push(VideoStream({
            magnetUrl: magnetUrl,
            timestamp: block.timestamp
        }));
        emit StreamStarted(msg.sender, magnetUrl, block.timestamp);
    }

    // Get the user's video history
    function getVideoHistory(address user) public view returns (VideoStream[] memory) {
        return profiles[user].streams;
    }

    // Get the user's profile (including CSS, HTML, and bio)
    function getProfile(address user) public view returns (string memory, string memory, string memory, string memory) {
        Profile memory profile = profiles[user];
        return (profile.name, profile.bio, profile.css, profile.html);
    }
}
