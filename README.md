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

You can install the tool using `pip` (or `uv`):

```bash
pip install convoviz
# or
uv pip install convoviz
```

### 3. Run the Script 🏃‍♂️

You have two options: **Interactive Mode** or **Command Line Arguments**.

#### Interactive Mode

Simply run the command and follow the prompts:

```bash
convoviz
```

#### Command Line Arguments

You can provide arguments directly to skip the prompts:

```bash
convoviz --zip path/to/your/export.zip --output path/to/output/folder
```

For more options, run:

```bash
convoviz --help
```

### 4. Check the Output 🎉

And that's it! After running the script, head over to the output folder to see your nice word clouds, graphs, and neatly formatted Markdown files. Enjoy !

## Share Your Feedback! 💌

I hope you find this tool useful. I'm continuously looking to improve on this, but I need your help for that.

Whether you're a tech wizard or you're new to all this, I'd love to hear about your journey with the tool. Found a quirk? Have a suggestion? Or just want to send some good vibes? I'm all ears!

**Here's how you can share your thoughts:**

1. **GitHub Issues**: For more specific feedback or if you've stumbled upon a bug, please open an [issue](https://github.com/mohamed-chs/chatgpt-history-export-to-md/issues). This helps me track and address them effectively.

2. **GitHub Discussions**: If you just want to share your general experience, have a suggestion, or maybe a cool idea for a new feature, jump into the [discussions](https://github.com/mohamed-chs/chatgpt-history-export-to-md/discussions) page. It's a more casual space where we can chat.

And if you've had a great experience, consider giving the project a star ⭐. It keeps me motivated and helps others discover it!

Thank you for being awesome! 🌟

## Notes

This project requires Python 3.9 or higher.

This is just a small thing I coded to help me see my convos in beautiful markdown, in [Obsidian](https://obsidian.md/) (my go-to note-taking app).

It also works as package, so you can **import** it in your own projects, and use the models and functions as you wish.