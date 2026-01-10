# Convoviz 📊: Visualize your entire ChatGPT data

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

Try it without installing using uv ([astral-sh/uv](https://github.com/astral-sh/uv)):

```bash
uvx convoviz
```

You can install it with uv (Recommended):

```bash
uv tool install convoviz
```

or pipx:
```bash
pipx install convoviz
```

### 3. Run the tool 🏃‍♂️

Simply run the command and follow the prompts:

```bash
convoviz
```

#### Command Line Arguments

You can provide arguments directly to skip the prompts:

```bash
convoviz --input path/to/your/export.zip --output path/to/output/folder
```

Inputs can be any of:
- A ChatGPT export ZIP (downloaded from OpenAI)
- An extracted export directory containing `conversations.json`
- A `conversations.json` file directly

Notes:
- `--zip` / `-z` is kept as an alias for `--input` for convenience.
- You can force non-interactive mode with `--no-interactive`.

For more options, run:

```bash
convoviz --help
```

### 4. Check the Output 🎉

And that's it! After running the script, head over to the output folder to see your neatly formatted Markdown files and visualizations.

The main outputs are:

- **`Markdown/`**: one `.md` file per conversation
- **`Graphs/`**: a small set of high-signal plots, including:
  - `overview.png` (dashboard)
  - `activity_heatmap.png` (weekday × hour)
  - `daily_activity.png` / `monthly_activity.png`
  - `model_usage.png`, `conversation_lengths.png`
  - `weekday_pattern.png`, `hourly_pattern.png`, `conversation_lifetimes.png`
- **`Word-Clouds/`**: weekly/monthly/yearly word clouds
- **`custom_instructions.json`**: extracted custom instructions

## Share Your Feedback! 💌

I hope you find this tool useful. I'm continuously looking to improve on this, but I need your help for that.

Whether you're a tech wizard or you're new to all this, I'd love to hear about your journey with the tool. Found a quirk? Have a suggestion? Or just want to send some good vibes? I'm all ears!

**Here's how you can share your thoughts:**

1. **GitHub Issues**: For more specific feedback or if you've stumbled upon a bug, please open an [issue](https://github.com/mohamed-chs/chatgpt-history-export-to-md/issues). This helps me track and address them effectively.

2. **GitHub Discussions**: If you just want to share your general experience, have a suggestion, or maybe a cool idea for a new feature, jump into the [discussions](https://github.com/mohamed-chs/chatgpt-history-export-to-md/discussions) page. It's a more casual space where we can chat.

And if you've had a great experience, consider giving the project a star ⭐. It keeps me motivated and helps others discover it!

## Notes

This is just a small thing I coded to help me see my convos in beautiful markdown. It was originally built with [Obsidian](https://obsidian.md/) (my go-to note-taking app) in mind, but the default output is standard Markdown (and you can choose an Obsidian-flavored mode in the interactive config if you want block IDs / navigation links).

I wasn't a fan of the clunky, and sometimes paid, browser extensions.

It was also a great opportunity to learn more about Python and type annotations. I had mypy, pyright, and ruff all on strict mode, 'twas fun.

It should(?) also work as library, so you can import and use the models and functions. I need to add more documentation for that tho. Feel free to reach out if you need help.

### Offline / reproducible runs

Convoviz uses NLTK stopwords for word clouds. If you’re offline and NLTK data isn’t already installed, pre-download it once:

```bash
python -c "import nltk; nltk.download('stopwords')"
```

If you’re using `uv` without a global install, you can run:

```bash
uv run python -c "import nltk; nltk.download('stopwords')"
```

### Bookmarklet

There’s also a JavaScript bookmarklet flow under `js/` (experimental) for exporting additional conversation data outside the official ZIP export.
