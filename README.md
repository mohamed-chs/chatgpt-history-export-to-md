# Convoviz 📊: Visualize your entire ChatGPT data !

Convert your ChatGPT history into well-formatted Markdown files. Additionally, visualize your data with word clouds 🔡☁️, view your prompt history graphs 📈, and access all your custom instructions 🤖 in a single location.

![GitHub last commit](https://img.shields.io/github/last-commit/mohamed-chs/chatgpt-history-export-to-md)
![GitHub issues](https://img.shields.io/github/issues/mohamed-chs/chatgpt-history-export-to-md)

## Features

- **YAML Headers**: Optional and included by default.
- **Track message versions**: prompt/response edits included.
- **Code Interpreter**: Environment code blocks and execution results.
- **Data Visualizations**: Word clouds, graphs, and more.
- **Custom Instructions**: All your custom instructions in one JSON file.

See examples [here](demo).

## How to Use 📖

### 1. Export Your ChatGPT Data 🗂

- Sign in at [chat.openai.com](https://chat.openai.com).
- Navigate: Profile Name (bottom left) -> **Settings** -> **Data controls** -> **Export** -> **Confirm export**.
- Await email from OpenAI and download the `.zip` file.

### 2. Install the tool 🛠

Open a terminal or command prompt and run:

```bash
pip install convoviz
```

to install the package.

### 3. Run the Script 🏃‍♂️

With the package installed, run the following command in your terminal:

```bash
python -m convoviz
```

Next, follow the instructions displayed and choose your desired options, the script will handle the rest.

### 4. Check the Output 🎉

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

## Notes

This project requires Python 3.8.7 or higher if on Windows. See [known issue](https://github.com/prompt-toolkit/python-prompt-toolkit/issues/1023#issue-534396318)

This is just a small thing I coded to help me see my convos in beautiful markdown, in [Obsidian](https://obsidian.md/) (my go-to note-taking app).

I wasn't a fan of the clunky, and sometimes paid, browser extensions.

It was also a great opportunity to learn more about Python and type annotations. I had mypy, pyright, and ruff all on strict mode, 'twas fun.

It also works as package, so you can **import** it in your own projects, and use the models and functions as you wish. I need to add more documentation for that tho. Feel free to reach out if you need help.

I'm working on automating it to add new conversations and updating old ones. Had some luck with a JavaScript bookmarklet, still ironing it out tho. Shouldn't take long.

> for an older version with zero dependencies, see https://github.com/mohamed-chs/chatgpt-history-export-to-md/tree/fe13a701fe8653c9f946b1e12979ce3bfe7104b8.
