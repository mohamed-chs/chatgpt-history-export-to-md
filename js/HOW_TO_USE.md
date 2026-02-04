# How to Use the Convoviz Bookmarklet Script

This script allows you to quickly download your recent ChatGPT conversations and assets directly from your browser, without waiting for the official data export email.

## 📥 How to Use

The fastest way to use this script is to run it directly in your browser's developer console.

1.  **Open ChatGPT**: Go to [chatgpt.com](https://chatgpt.com) and ensure you are logged in.
2.  **Open Developer Tools**:
    *   Press `F12` (or `Cmd + Option + I` on Mac).
    *   Click the **Console** tab.
3.  **Copy & Paste**:
    *   Open [`script.js`](script.js) and copy the entire content.
    *   Paste it into the console and press **Enter**.
4.  **Configure & Start**:
    *   A small popup will appear in the top-right corner.
    *   Enter the number of recent conversations to fetch and click **Start**.
5.  **Download**: The script will download a `chatgpt_bookmarklet_download.json` file and any associated images/attachments.
    *   *Note: If your browser asks for permission to download multiple files, click "Allow".*

---

## 🔖 Alternative: Bookmarklet Method

If you plan to use this frequently, you can save it as a bookmark:

1.  **Create Bookmark**: Right-click your bookmarks bar -> "Add page" (or "Add Bookmark").
2.  **Name**: "Convoviz Export".
3.  **URL**: Type `javascript:` and then paste the entire code from [`script.js`](script.js).
    *   It should look like `javascript:(async () => { ... })();`.
4.  **Usage**: Just click this bookmark while on the ChatGPT site to trigger the popup.

---

## 🛠️ Importing into Convoviz

### The "Zero-Config" Method (Recommended)
If you already have an official ChatGPT export ZIP file, you don't need to do anything! 

1.  Keep the `chatgpt_bookmarklet_download.json` and images in your `Downloads` folder.
2.  Run `convoviz` on your official export:
    ```bash
    convoviz --input ~/Downloads/official-export.zip
    ```
3.  **Convoviz will automatically find the bookmarklet data**, merge the latest conversations, and link the images directly from your `Downloads` folder.

### The Manual Method
If you *only* want to process the bookmarklet data:

1.  **Move Files**: Move the JSON and images into a single folder (e.g., `~/Documents/ChatGPT-Latest`).
2.  **Run**: Point `convoviz` directly to the JSON file:
    ```bash
    convoviz --input ~/Documents/ChatGPT-Latest/chatgpt_bookmarklet_download.json
    ```

## ⚠️ Important Notes

*   **Rate Limits**: If you request too many conversations at once (e.g., >100), OpenAI might temporarily rate-limit you. The script tries to handle this by waiting, but it's best to grab smaller batches.
*   **Assets**: Ensure you keep the JSON file and the downloaded image files in the same directory so `convoviz` can find them.
*   **Experimental**: This script relies on ChatGPT's internal API, which changes frequently. If it stops working, please [open an issue](https://github.com/mohamed-chs/convoviz/issues).
