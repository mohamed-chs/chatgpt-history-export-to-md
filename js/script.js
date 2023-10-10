// --- CSS / UI definitions ---

const styles = {
  toggleUI: `
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
  `,
  downloadWidget: `
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
  `,
};

const toggleUIHTML = `
<button id="toggle-openai-ui" style="${styles.toggleUI}">⏬</button>
`;

const uiHTML = `
<div id="openai-download-widget" style="${styles.downloadWidget}">
  <div style="margin-bottom: 15px">
    <label for="numConversations" style="display: block; margin-bottom: 5px; font-weight: 600">Number of conversations:</label>
    <input type="number" id="numConversations" value="50" style="width: 100%; padding: 5px; border: 1px solid #ccc; border-radius: 5px; box-sizing: border-box;" />
  </div>
  <div style="margin-bottom: 15px">
    <label for="openai-download-progress" style="display: block; margin-bottom: 5px; font-weight: 600">Download Progress:</label>
    <progress id="openai-download-progress" value="0" max="100" style="width: 100%; height: 15px; border-radius: 5px"></progress>
  </div>
  <div style="text-align: left">
    <button id="openai-start-download" style="padding: 10px 15px; background-color: #007bff; color: #fff; border: none; border-radius: 5px; cursor: pointer;">Start Download</button>
  </div>
</div>
`;

// Append UI components
document.body.insertAdjacentHTML("beforeend", toggleUIHTML + uiHTML);

// --- Utility functions ---

const toggleUIVisibility = () => {
  const uiWidget = document.getElementById("openai-download-widget");
  uiWidget.style.display = uiWidget.style.display === "none" ? "block" : "none";
};

function constructUrlWithParams(baseUrl, params) {
  const url = new URL(baseUrl);
  Object.keys(params).forEach((key) =>
    url.searchParams.append(key, params[key])
  );
  return url.toString();
}

// --- Event Listeners ---

document
  .getElementById("toggle-openai-ui")
  .addEventListener("click", toggleUIVisibility);
document
  .getElementById("openai-start-download")
  .addEventListener("click", async () => {
    const numConversations = parseInt(
      document.getElementById("numConversations").value,
      10
    );

    if (numConversations && numConversations > 0) {
      document.getElementById("openai-start-download").disabled = true;
      try {
        await downloadConversationsAsJson(numConversations);
        console.log("Download completed.");
      } catch (error) {
        console.error("An error occurred:", error);
      }
      document.getElementById("openai-start-download").disabled = false;
    } else {
      alert("Please enter a valid number of conversations.");
    }
  });

// --- Main functionality ---

const conversationsPerRequest = 50;
const delay = 63000;

async function fetchData(url, headers = {}) {
  try {
    const response = await fetch(url, { headers });
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error(`Error fetching data from ${url}:`, error);
    throw error;
  }
}

async function fetchAccessToken() {
  const data = await fetchData("https://chat.openai.com/api/auth/session");
  return data.accessToken;
}

async function fetchConversationsData(accessToken, limit, offset) {
  const baseUrl = "https://chat.openai.com/backend-api/conversations";
  const url = constructUrlWithParams(baseUrl, {
    offset: offset,
    limit: limit,
    order: "updated",
  });
  const data = await fetchData(url, { Authorization: `Bearer ${accessToken}` });
  return data.items;
}

async function fetchConversationData(accessToken, conversationId) {
  const url = `https://chat.openai.com/backend-api/conversation/${conversationId}`;
  return fetchData(url, { Authorization: `Bearer ${accessToken}` });
}

async function downloadConversationsAsJson(numConversations) {
  const conversationsArray = [];
  const accessToken = await fetchAccessToken();

  const numRequests = Math.ceil(numConversations / conversationsPerRequest);
  for (let i = 0; i < numRequests; i++) {
    const offset = i * conversationsPerRequest;
    const limit =
      i === numRequests - 1
        ? numConversations - offset
        : conversationsPerRequest;

    const conversationsData = await fetchConversationsData(
      accessToken,
      limit,
      offset
    );
    for (let j = 0; j < conversationsData.length; j++) {
      const conversation = conversationsData[j];
      const conversationData = await fetchConversationData(
        accessToken,
        conversation.id
      );
      conversationsArray.push(conversationData);

      const progress =
        ((i * conversationsPerRequest + j + 1) / numConversations) * 100;
      document.getElementById("openai-download-progress").value = progress;
    }

    if (i < numRequests - 1) {
      await new Promise((resolve) => setTimeout(resolve, delay));
    }
  }

  const content = new Blob([JSON.stringify(conversationsArray)], {
    type: "application/json",
  });
  const a = document.createElement("a");
  a.href = URL.createObjectURL(content);
  a.download = "chatgpt_bookmarklet_download.json";
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
}
