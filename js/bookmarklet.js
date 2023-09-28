const toggleUIHTML = `
  <button id="toggle-openai-ui" style="
    position: fixed; 
    bottom: 20px; 
    right: 20px; 
    padding: 10px; 
    background-color: #007BFF; 
    border: none; 
    border-radius: 50%; 
    color: white; 
    font-weight: bold; 
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.25); 
    cursor: pointer; 
    z-index: 10000;
    ">
    ⏬
  </button>
`;

document.body.insertAdjacentHTML("beforeend", toggleUIHTML);

document.getElementById("toggle-openai-ui").addEventListener("click", () => {
  const uiWidget = document.getElementById("openai-download-widget");
  if (uiWidget.style.display === "none") {
    uiWidget.style.display = "block";
  } else {
    uiWidget.style.display = "none";
  }
});

// Define a string containing HTML code to create a user interface (UI) for the download widget
const uiHTML = `
<div id="openai-download-widget" style="
position: fixed;
bottom: 10px;
right: 10px;
background: #fff;
border: 1px solid #ccc;
padding: 20px;
border-radius: 10px;
z-index: 9999;
width: 300px;
box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
">
<div style="margin-bottom: 15px">
<label for="numConversations" style="display: block; margin-bottom: 5px; font-weight: 600">
  Number of conversations:
</label>
<input type="number" id="numConversations" value="50" style="
    width: 100%;
    padding: 5px;
    border: 1px solid #ccc;
    border-radius: 5px;
    box-sizing: border-box;
  " />
</div>
<div style="margin-bottom: 15px">
<label for="openai-download-progress" style="display: block; margin-bottom: 5px; font-weight: 600">
  Download Progress:
</label>
<progress id="openai-download-progress" value="0" max="100"
  style="width: 100%; height: 15px; border-radius: 5px"></progress>
</div>
<div style="text-align: left">
<button id="openai-start-download" style="
    padding: 10px 15px;
    background-color: #007bff;
    color: #fff;
    border: none;
    border-radius: 5px;
    cursor: pointer;
  ">
  Start Download
</button>
</div>
</div>
`;

// Append the download widget HTML code to the end of the body section of the webpage
document.body.insertAdjacentHTML("beforeend", uiHTML);

// Add a 'click' event listener to the "Start Download" button to trigger the function that validates the input and starts the download process
document
  .getElementById("openai-start-download")
  .addEventListener("click", () => {
    // Get the number of conversations to be downloaded from the input field and convert it to an integer
    const numConversations = parseInt(
      document.getElementById("numConversations").value,
      10
    );
    // Check if the number of conversations entered is a positive number
    if (numConversations && numConversations > 0) {
      // If valid, hide the widget and start the download process
      document.getElementById("openai-start-download").disabled = true; // Disable the button
      downloadConversationsAsZip(numConversations); // Start the download process
    } else {
      // If not valid, show an alert message to the user
      alert("Please enter a valid number of conversations.");
    }
  });

// Define constants for the number of conversations to fetch per request and the delay between requests
const conversationsPerRequest = 50;
const delay = 63000; // Wait for 63 seconds ( > ~ 1 minute)

// Function to make an API request and handle any errors that may occur during the request
async function fetchData(url, accessToken) {
  try {
    const response = await fetch(url, {
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
    });
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error(`Error fetching data from ${url}:`, error);
    throw error;
  }
}

// Function to fetch the access token needed to authenticate API requests
async function fetchAccessToken(url) {
  const data = await fetchData(url);
  return data.accessToken;
}

// Function to fetch a paginated list of conversations data from the API
async function fetchConversationsData(accessToken, limit, offset) {
  const baseUrl = "https://chat.openai.com/backend-api/conversations";
  const queryParams = {
    offset: offset,
    limit: limit,
    order: "updated",
  };

  // Construct the full URL with query parameters
  const url = constructUrlWithParams(baseUrl, queryParams);

  const data = await fetchData(url, accessToken);
  return data.items; // Return the items array
}

// Helper function to construct a URL with query parameters for API requests
function constructUrlWithParams(baseUrl, params) {
  const url = new URL(baseUrl);
  Object.keys(params).forEach((key) =>
    url.searchParams.append(key, params[key])
  );
  return url.toString();
}

// Function to fetch the data of a specific conversation using its ID
async function fetchConversationData(accessToken, conversationId) {
  const url = `https://chat.openai.com/backend-api/conversation/${conversationId}`;
  return fetchData(url, accessToken);
}

// Main function to download a specified number of conversations as a .zip file
async function downloadConversationsAsZip(numConversations) {
  // Calculate the number of API requests needed to fetch all conversations
  const numRequests = Math.ceil(numConversations / conversationsPerRequest);
  try {
    // Create a new JSZip instance
    const zip = new JSZip();

    // Fetch the access token
    const accessToken = await fetchAccessToken(
      "https://chat.openai.com/api/auth/session"
    );

    // Fetch and download conversations in batches
    for (let i = 0; i < numRequests; i++) {
      const offset = i * conversationsPerRequest;

      // Determine the number of conversations to fetch in the current batch
      const limit =
        i === numRequests - 1
          ? numConversations - offset
          : conversationsPerRequest;

      // Fetch the current batch of conversations data
      const conversationsData = await fetchConversationsData(
        accessToken,
        limit,
        offset
      );

      // Log the progress
      console.log(`Fetched ${conversationsData.length} conversations.`);

      // Add each conversation to the zip file
      for (let j = 0; j < conversationsData.length; j++) {
        const conversation = conversationsData[j];
        const conversationData = await fetchConversationData(
          accessToken,
          conversation.id
        );
        const fileName = `conversation_${conversation.id}.json`;
        zip.file(fileName, JSON.stringify(conversationData));
        console.log(`Added ${fileName} to the zip file.`);

        // Update the download progress bar after each conversation is added to the zip file
        const progress =
          ((i * conversationsPerRequest + j + 1) / numConversations) * 100;
        document.getElementById("openai-download-progress").value = progress;
      }

      // Wait for a moment to avoid hitting the API rate limits (calculated to be about ~ 60 / minute, then a 1 minute timeout)
      if (i < numRequests - 1) {
        await new Promise((resolve) => setTimeout(resolve, delay)); // Wait for 63 seconds ( > ~ 1 minute)
      }
    }

    // Generate the zip file and start the download
    zip.generateAsync({ type: "blob" }).then(function (content) {
      const a = document.createElement("a");
      a.href = URL.createObjectURL(content);
      a.download = "conversations_data.zip";
      a.style.display = "none";
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);

      // Log the completion
      console.log("Download completed.");

      document.getElementById("openai-start-download").disabled = false; // Re-enable the button
    });
  } catch (error) {
    console.error("An error occurred:", error);
    document.getElementById("openai-start-download").disabled = false; // Re-enable the button in case of error
  }
}
