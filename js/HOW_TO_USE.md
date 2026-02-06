# ChatGPT Direct Export

Export recent conversations and assets directly from your browser—no waiting for OpenAI emails. This method now packages everything into a single `.zip` file for convenience.

## 📥 Usage (Console)
1.  **Open ChatGPT**: Log in at [chatgpt.com](https://chatgpt.com).
2.  **Open Console**: Press `F12` (or `Cmd + Opt + I`) and click the **Console** tab.
3.  **Load JSZip**: Copy/paste the content of the JSZip library (e.g., from [cdnjs](https://cdnjs.cloudflare.com/ajax/libs/jszip/3.10.1/jszip.min.js)) into the console and hit **Enter**.
4.  **Run Script**: Copy/paste the entire content of [`script.js`](script.js) into the console and hit **Enter**.
5.  **Export**: Enter the number of conversations in the popup and click **Start**.
    *   *Result: A single `convoviz_export.zip` file will be downloaded.*

---

## 🔖 Bookmarklet Method
For frequent use, save a bookmark with the name "Convoviz Export" and the URL:
`javascript:` + (paste `script.js` content here)
*Note: You still need to run the JSZip script once per session if it hasn't been loaded.*

---

## 🛠️ Importing into Convoviz

### Option A: Merge with Official Export (Recommended)
Keep the `convoviz_export.zip` in your `Downloads` and run `convoviz` on your official ZIP. You'll be prompted to merge the recent data automatically.

### Option B: Direct Input
Point `convoviz` directly to the exported ZIP:
```bash
convoviz --input ~/Downloads/convoviz_export.zip
```

---

## ⚠️ Notes
*   **Rate Limits**: Avoid fetching hundreds of chats at once.
*   **Experimental**: Relies on internal APIs; if it breaks, [open an issue](https://github.com/mohamed-chs/convoviz/issues).
