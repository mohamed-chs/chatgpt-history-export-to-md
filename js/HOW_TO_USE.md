# ChatGPT Bookmarklet Export

Export recent conversations and assets directly from your browser—no waiting for OpenAI emails.

## 📥 Usage (Console)
1.  **Open ChatGPT**: Log in at [chatgpt.com](https://chatgpt.com).
2.  **Open Console**: Press `F12` (or `Cmd + Opt + I`) and click the **Console** tab.
3.  **Run Script**: Copy/paste the entire content of [`script.js`](script.js) into the console and hit **Enter**.
4.  **Export**: Enter the number of conversations in the popup and click **Start**.
    *   *Note: If your browser warns about multiple downloads, click **Allow**.*

---

## 🔖 Bookmarklet Method
For frequent use, save a bookmark with the name "Convoviz Export" and the URL:
`javascript:` + (paste `script.js` content here)

---

## 🛠️ Importing into Convoviz

### Option A: Merge with ZIP (Recommended)
Keep the JSON and images in `Downloads` and run `convoviz` on your ZIP. You'll be prompted to merge the recent data automatically.

### Option B: Bookmarklet Only
Move the files to a folder and point `convoviz` to the JSON:
```bash
convoviz --input path/to/chatgpt_bookmarklet_download.json
```

---

## ⚠️ Notes
*   **Assets**: Keep the JSON and images together for correct rendering.
*   **Rate Limits**: Avoid fetching hundreds of chats at once.
*   **Experimental**: Relies on internal APIs; if it breaks, [open an issue](https://github.com/mohamed-chs/convoviz/issues).
