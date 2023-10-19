# Your entire ChatGPT data in beautiful Markdown 📜

Convert your ChatGPT history into well-formatted Markdown files. Additionally, visualize your data with word clouds 🔡☁️, view your prompt history graphs 📈, and access all your custom instructions 🤖 in a single location.

![GitHub last commit](https://img.shields.io/github/last-commit/mohamed-chs/chatgpt-history-export-to-md)
![GitHub issues](https://img.shields.io/github/issues/mohamed-chs/chatgpt-history-export-to-md)

## Features

- **YAML Headers**: Optional and included by default.
- **Track message versions**: prompt/response edits included.
- **Code Interpreter**: Environment code blocks and execution results.
- **Data Visualizations**: Word clouds, graphs, and more.
- **Custom Instructions**: All your custom instructions in one JSON file.

See examples [here](assets/demo).

## Getting Started

Ensure you have **Python** and **Git** installed. If not:

- [Python](https://www.python.org/downloads/)
- [Git](https://git-scm.com/downloads)

### 1. Export Your ChatGPT Data 🗂

- Sign in at [chat.openai.com](https://chat.openai.com).
- Navigate: Profile Name (bottom left) -> **Settings** -> **Data controls** -> **Export** -> **Confirm export**.
- Await email from OpenAI and download the `.zip` file.

### 2. Copy the Tool to Your Computer 📥

- Open a program called "terminal" or "command prompt".

- Type (and hit enter after each line):

```bash
git clone https://github.com/mohamed-chs/chatgpt-history-export-to-md.git
```

```bash
cd chatgpt-history-export-to-md
```

This will copy this GitHub repository on your computer, and navigate to the root directory.

### 3. Set Up the Environment 🛠️

Type (and hit enter):

```bash
python setup.py
```

This will create a virtual environment and install the necessary python libraries.

#### Activate the virtual environment

**On Linux or MacOS:**

```bash
source .venv/bin/activate
```

**On Windows:**

Using Command Prompt (`cmd.exe`):

```bash
.venv\Scripts\activate.bat
```

Using PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

If you encounter an error about script execution in PowerShell, try running:

```powershell
powershell -ExecutionPolicy ByPass -File .venv\Scripts\Activate.ps1
```

### 4. Run the Script 🏃‍♂️

With the environment set up, you can now run the script. In the terminal or command prompt, execute:

```bash
python cli.py
```

Now, follow the instructions on screen and choose your desired options, the script will handle the rest.

### 5. Check the Output 🎉

And that's it! After running the script, head over to the output folder to see your nice word clouds, graphs, and neatly formatted Markdown files. Enjoy !

**Tweet Your Discoveries**:

[![Tweet](https://img.shields.io/twitter/url?style=social&url=https%3A%2F%2Fgithub.com%2Fyourusername%2Fyourrepository)](https://twitter.com/intent/tweet?text=So%2C%20this%20is%20what%20my%20entire%20ChatGPT%20history%20looks%20like%20...%0D%0A%0D%0Ahttp%3A%2F%2Fbit.ly%2F3ZuHCCK)

### How to add new conversations ➕

See [How to use the JS script](js/how_to_use.md) for instructions on how to download new conversations.

## Share Your Feedback! 💌

I hope you find this tool useful. I'm continuously looking to improve on this, but I need your help for that.

Whether you're a tech wizard or you're new to all this (especially if you're new to all this), I'd love to hear about your journey with the tool. Found a quirk? Have a suggestion? Or just want to send some good vibes? I'm all ears!

**Here's how you can share your thoughts:**

1. **GitHub Issues**: For more specific feedback or if you've stumbled upon a bug, please open an [issue](https://github.com/mohamed-chs/chatgpt-history-export-to-md/issues). This helps me track and address them effectively.

2. **GitHub Discussions**: If you just want to share your general experience, have a suggestion, or maybe a cool idea for a new feature, jump into the [discussions](https://github.com/mohamed-chs/chatgpt-history-export-to-md/discussions) page. It's a more casual space where we can chat.

And if you've had a great experience, consider giving the project a star ⭐. It keeps me motivated and helps others discover it!

Thank you for being awesome! 🌟

## Contributions 🆘

Feel free to fork this repository and make your enhancements or improvements. ALL contributions are welcome !

See [contributing guide](CONTRIBUTING.md)

> [Related post](https://news.ycombinator.com/item?id=37636701)

## Notes

This is just a small thing I coded to help me see my convos in beautiful markdown, in [Obsidian](https://obsidian.md/) (my go-to note-taking app).

I wasn't a fan of the clunky, and sometimes paid, browser extensions.

I'm working on automating it to add new conversations and updating old ones. Had some luck with a JavaScript bookmarklet, still ironing it out tho. Shouldn't take long.

See [TODO](TODO.md) for more info on what I'm working on. Feel free to contribute :)

> for an older version with no external dependencies (no virtual environment needed), see https://github.com/mohamed-chs/chatgpt-history-export-to-md/tree/fe13a701fe8653c9f946b1e12979ce3bfe7104b8.
