let web3;
let gremlinDAO, gremlinThread, gremlinPost, sysAdmin, poster;
let userAddress;

async function fetchContractData() {
    const response = await fetch('/contract_data');
    const data = await response.json();
    return data;
}

async function connectWallet() {
    if (typeof window.ethereum !== 'undefined') {
        web3 = new Web3(window.ethereum);
        try {
            const accounts = await window.ethereum.request({ method: 'eth_requestAccounts' });
            userAddress = accounts[0];
            console.log("Connected to MetaMask:", userAddress);

            // Fetch contract data from Flask
            const contractData = await fetchContractData();

            // Initialize contract instances
            gremlinDAO = new web3.eth.Contract(contractData.gremlinDAOABI, contractData.gremlinDAOAddress);
            gremlinThread = new web3.eth.Contract(contractData.gremlinThreadABI, contractData.gremlinThreadAddress);
            gremlinPost = new web3.eth.Contract(contractData.gremlinPostABI, contractData.gremlinPostAddress);
            sysAdmin = new web3.eth.Contract(contractData.sysAdminContractABI, contractData.sysAdminContractAddress);
            poster = new web3.eth.Contract(contractData.posterABI, contractData.posterAddress);

            // Show SysAdmin actions
            document.getElementById('sysadminActions').style.display = 'block';
        } catch (error) {
            console.error("User denied account access");
        }
    } else {
        alert("MetaMask is not installed. Please install MetaMask to use this feature.");
    }
}

async function addModerator() {
    const moderatorAddress = prompt("Enter the address of the moderator:");
    if (moderatorAddress) {
        try {
            await sysAdmin.methods.addModerator(moderatorAddress).send({ from: userAddress });
            alert("Moderator added successfully.");
        } catch (error) {
            console.error("Error adding moderator:", error);
        }
    }
}

async function blacklistThread() {
    const threadId = prompt("Enter the Thread ID to blacklist:");
    if (threadId) {
        try {
            await sysAdmin.methods.blacklistThread(threadId).send({ from: userAddress });
            alert("Thread blacklisted successfully.");
        } catch (error) {
            console.error("Error blacklisting thread:", error);
        }
    }
}

async function setMaxSupply() {
    const newMaxSupply = prompt("Enter the new max supply:");
    if (newMaxSupply) {
        try {
            await gremlinDAO.methods.setMaxSupply(newMaxSupply).send({ from: userAddress });
            alert("Max supply set successfully.");
        } catch (error) {
            console.error("Error setting max supply:", error);
        }
    }
}

// Event Listeners
document.getElementById('connectWalletBtn').addEventListener('click', connectWallet);
document.getElementById('addModeratorBtn').addEventListener('click', addModerator);
document.getElementById('blacklistThreadBtn').addEventListener('click', blacklistThread);
document.getElementById('setMaxSupplyBtn').addEventListener('click', setMaxSupply);
