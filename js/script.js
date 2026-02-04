/**
 * convoviz script
 * A simple tool to grab your ChatGPT chats and media in bulk.
 */

(async () => {
  // --- 1. SETTINGS ---
  const CONFIG = {
    CONCURRENCY: 3, // How many chats to fetch at once
    BATCH_SIZE: 50, // How many to ask for per page
    JSON_FILENAME: "chatgpt_bookmarklet_download.json",
    COLORS: {
      bg: "rgba(32, 33, 35, 0.95)",
      accent: "#10a37f",
      text: "#ececf1",
      border: "#4d4d4f",
    },
  };

  // --- 2. DATA TRACKING ---
  const State = {
    token: "",
    results: [],
    totalToFetch: 0,
    completed: 0,
    isRunning: false,
    abortController: null,
  };

  // --- 3. INTERFACE (The Popup) ---
  const UI = {
    container: null,

    // Put the UI on the screen
    inject() {
      if (document.getElementById("convoviz-ui")) return;

      this.container = document.createElement("div");
      this.container.id = "convoviz-ui";
      this.container.style = `
                position: fixed; top: 20px; right: 20px; width: 280px;
                background: ${CONFIG.COLORS.bg}; color: ${CONFIG.COLORS.text};
                backdrop-filter: blur(10px); border: 1px solid ${CONFIG.COLORS.border};
                border-radius: 12px; padding: 16px; z-index: 10000;
                font-family: -apple-system, Segoe UI, Roboto, sans-serif;
                box-shadow: 0 12px 24px rgba(0,0,0,0.3); transition: all 0.3s ease;
            `;

      this.render("setup");
      document.body.appendChild(this.container);
    },

    // Toggle between "ready" and "working" views
    render(phase) {
      const html = {
        setup: `
                    <div style="font-weight: 600; margin-bottom: 12px; display: flex; align-items: center;">
                        <span style="background: ${CONFIG.COLORS.accent}; width: 8px; height: 8px; border-radius: 50%; margin-right: 8px;"></span>
                        convoviz script
                    </div>
                    <div style="display: flex; gap: 8px;">
                        <input type="number" id="arch-count" value="50" style="flex: 1; background: #343541; border: 1px solid ${CONFIG.COLORS.border}; color: white; padding: 6px; border-radius: 6px; font-size: 13px;">
                        <button id="arch-start" style="background: ${CONFIG.COLORS.accent}; color: white; border: none; padding: 6px 12px; border-radius: 6px; cursor: pointer; font-weight: 600; font-size: 13px;">Start</button>
                    </div>
                `,
        active: `
                    <div id="arch-status" style="font-size: 12px; margin-bottom: 8px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">Starting up...</div>
                    <div style="width: 100%; background: #343541; height: 6px; border-radius: 3px; overflow: hidden; margin-bottom: 12px;">
                        <div id="arch-bar" style="width: 0%; height: 100%; background: ${CONFIG.COLORS.accent}; transition: width 0.3s;"></div>
                    </div>
                    <button id="arch-stop" style="width: 100%; background: transparent; border: 1px solid #ef4444; color: #ef4444; padding: 4px; border-radius: 6px; cursor: pointer; font-size: 11px;">Stop</button>
                `,
      };

      this.container.innerHTML = html[phase === "active" ? "active" : "setup"];

      if (phase === "setup") {
        this.container.querySelector("#arch-start").onclick = () =>
          Core.start();
      } else {
        this.container.querySelector("#arch-stop").onclick = () =>
          location.reload();
      }
    },

    // Update progress bar and text
    update(msg, progress) {
      const status = document.getElementById("arch-status");
      const bar = document.getElementById("arch-bar");
      if (status) status.innerText = msg;
      if (bar) bar.style.width = `${progress}%`;
    },
  };

  // --- 4. DATA FETCHERS ---
  const Net = {
    async wait(ms) {
      return new Promise((r) => setTimeout(r, ms));
    },

    // Wrapper for fetch that handles auth and rate limits
    async fetchJson(url, options = {}) {
      const resp = await fetch(url, {
        ...options,
        headers: { ...options.headers, Authorization: `Bearer ${State.token}` },
      });

      // If OpenAI tells us to slow down, wait 10 seconds and try again
      if (resp.status === 429) {
        UI.update(
          "Rate limited. Waiting 10s...",
          (State.completed / State.totalToFetch) * 100,
        );
        await this.wait(10000);
        return this.fetchJson(url, options);
      }

      if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
      return resp.json();
    },

    // Trigger a file download in the browser
    download(blob, name) {
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = name;
      a.click();
      URL.revokeObjectURL(url);
    },
  };

  // --- 5. THE MAIN LOGIC ---
  const Core = {
    async start() {
      if (State.isRunning) return;
      State.totalToFetch = parseInt(
        document.getElementById("arch-count").value,
      );
      State.isRunning = true;
      UI.render("active");

      try {
        // 1. Get the access token from the current session
        const session = await Net.fetchJson("/api/auth/session");
        State.token = session.accessToken;

        // 2. Build a list of conversation IDs
        UI.update("Scanning history...", 5);
        const chatList = [];
        let offset = 0;

        while (chatList.length < State.totalToFetch) {
          const limit = Math.min(
            CONFIG.BATCH_SIZE,
            State.totalToFetch - offset,
          );
          const data = await Net.fetchJson(
            `/backend-api/conversations?offset=${offset}&limit=${limit}&order=updated`,
          );
          if (!data.items?.length) break;
          chatList.push(...data.items);
          offset += data.items.length;
          if (data.items.length < limit) break;
        }

        // 3. Download details for each chat using workers for speed
        const queue = [...chatList];
        const workers = Array(CONFIG.CONCURRENCY)
          .fill(null)
          .map(async () => {
            while (queue.length > 0) {
              const item = queue.shift();
              try {
                UI.update(
                  `Saving: ${item.title}`,
                  (State.completed / chatList.length) * 100,
                );
                const detail = await Net.fetchJson(
                  `/backend-api/conversation/${item.id}`,
                );
                State.results.push(detail);
                await this.processMedia(detail);
              } catch (e) {
                console.error(`Failed to grab: ${item.title}`, e);
              } finally {
                State.completed++;
              }
              await Net.wait(500); // Small pause to be polite to the API
            }
          });

        await Promise.all(workers);

        // 4. Wrap it all up into a JSON file
        UI.update("Generating Final JSON...", 100);
        Net.download(
          new Blob([JSON.stringify(State.results)], {
            type: "application/json",
          }),
          CONFIG.JSON_FILENAME,
        );

        UI.update("✅ Done!", 100);
        await Net.wait(3000);
        UI.render("setup");
        State.isRunning = false;
      } catch (err) {
        UI.update("❌ Error: " + err.message, 0);
        console.error(err);
        State.isRunning = false;
      }
    },

    // Check for images or file attachments and download them too
    async processMedia(chatJson) {
      const files = [];
      Object.values(chatJson.mapping || {}).forEach((node) => {
        const msg = node.message;
        if (!msg) return;

        // Find standard attachments
        msg.metadata?.attachments?.forEach((a) =>
          files.push({ id: a.id, name: a.name }),
        );

        // Find DALL-E images or uploaded photos
        msg.content?.parts?.forEach((p) => {
          if (p.content_type === "image_asset_pointer") {
            files.push({
              id: p.asset_pointer.replace("sediment://", ""),
              name: null,
            });
          }
        });
      });

      for (const file of files) {
        try {
          const meta = await Net.fetchJson(
            `/backend-api/files/download/${file.id}`,
          );
          if (meta.download_url) {
            const bResp = await fetch(meta.download_url);
            const b = await bResp.blob();
            const ext = b.type.split("/")[1] || "bin";
            // Convoviz needs the ID in the filename to map it back to the conversation
            const fileName = file.name
              ? `${file.id}_${file.name}`
              : `${file.id}.${ext}`;
            Net.download(b, fileName);
            await Net.wait(1000);
          }
        } catch (e) {
          console.warn("Skipping a file, couldn't grab it:", file.id);
        }
      }
    },
  };

  UI.inject();
})();
