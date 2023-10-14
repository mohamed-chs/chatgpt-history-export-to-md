## How to use the JS script

- Go to the [ChatGPT website](https://chat.openai.com/)
- Open the browser developer console (F12 on Chrome, Ctrl+Shift+I on Firefox)
- Then, copy-paste [this code](script.js) and hit 'Enter'
- A small UI widget should pop up in the bottom right, choose the number of conversations you want to download and click "Start Download". Now wait for the download to finish.

Now your conversations should be in a JSON file named something like "chatgpt_bookmarklet_download.json".

Alternatively, you can create a bookmarklet with the code in [this file](bookmarklet.js) and click it when you're on the ChatGPT website. It will do the same thing as the above steps.

(You should refresh the page after the download finishes, to clear the UI widget and the console logs.)

Now, if you run the `main.py` script, it should recognize the new downloaded json file and add the conversations to the ones from the OpenAI export, that way ALL the conversations are converted to markdown files, as well as the other data visualizations stuff.

This is a very rudimentary js script, and it needs more error handling. I've tried it on Chrome, and it works so far.
Could break at anytime if OpenAI changes their data permissions or the `/backend-api/` API.

Feel free to modify the script to your liking. Would also appreciate sharing the modified version with others here via a PR.

### still working on

- [x] add support to add new conversations to the Markdown output folder
- [x] update old ones
- [ ] more seamless api rate limit handling (currently just pauses for a minute after ~50 chat downloads)
- [ ] update the data analysis and visualization
- [ ] better widget UI (add error messages and progress and such,
      so you can close the dev console and still be kept informed on the download process)
- [ ] add instructions on how to create a bookmarklet
      (how to minify the js script, make it url valid, then creating the bookmark in the browser.
      Maybe do all these in-house? but that might need the uglify-js npm dependency ...)
- [ ] more todos ...
