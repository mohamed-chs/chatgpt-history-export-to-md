## How to use the JS script

- Open the browser developer console
- First, load the JSZIP library by copy-pasting [this code](cdnjs.cloudflare.com_ajax_libs_jszip_3.10.1_jszip.min.js) in the console, and hit 'Enter'
- Then, past [this code](bookmarklet.js) and hit 'Enter'

This is a very rudimentary js script, and it needs more error handling. I've tried it on Chrome, and it works so far.
Could break at anytime if OpenAI changes their data permissions for the `/backend-api/` API.

Why can't I just use a CDN link in bookmarklet.js to load the JSZIP instead of having to copy-paste the code into the dev console first? Because of the Content Security Policy (CSP) on the chat.openai.com website.

Feel free to modify the script to your liking. Would also appreciate sharing the modified version with others here via a PR.

### still working on

- [ ] add support to add new conversations to the Markdown output folder
- [ ] update old ones
- [ ] update the data analysis and visualization
- [ ] better widget UI (added error messages and progress and such,
so you can close the dev console and still be kept informed on the process)
- [ ] add instructions on how to create a bookmarklet
(how to minify the js script, make it url valid, then creating the bookmark in the browser.
Maybe do all these in-house? but that might need the uglify-js npm dependency ...)
- [ ] more todos ...
