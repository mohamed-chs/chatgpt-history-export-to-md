# Convoviz 📊: Visualize your entire ChatGPT data

Convert your ChatGPT history into well-formatted Markdown files. Visualize your data with word clouds 🔡☁️ and usage graphs 📈.

## Features

- **YAML Headers**: Optional and included by default.
- **Inline Images**: Media attachments rendered directly in Markdown.
- **Data Visualizations**: Word clouds, graphs, and more.

See examples [here](demo).

## How to Use 📖

### 1. Export Your ChatGPT Data 🗂

- Sign in at [chatgpt.com](https://chatgpt.com).
- Navigate: Profile Name (bottom left) -> **Settings** -> **Data controls** -> **Export** -> **Confirm export**.
- Await email from OpenAI and download the `.zip` file.

### 2. Install the tool 🛠

One command to install everything:

**Linux / macOS:**

```bash
curl -fsSL https://raw.githubusercontent.com/mohamed-chs/convoviz/main/install.sh | bash
```

**Windows (PowerShell):**

```powershell
irm https://raw.githubusercontent.com/mohamed-chs/convoviz/main/install.ps1 | iex
```

This installs [uv](https://github.com/astral-sh/uv) (if needed) and convoviz with graphs and word clouds.

#### Alternative: pip

```bash
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install "convoviz[viz]"
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

##### Selective Output

By default, all outputs are generated. Use `--outputs` to pick specific ones:

```bash
convoviz --input export.zip --outputs markdown --outputs graphs
```

Options: `markdown`, `graphs`, `wordclouds`. In interactive mode, you'll be prompted.

##### Other Notes

- `--zip` / `-z` is kept as an alias for `--input` for convenience.
- You can force non-interactive mode with `--no-interactive`.
- Use `--flat` to put all Markdown files in a single folder instead of organizing by date.
- Use `--verbose` or `-v` for detailed logging (use `-vv` for debug logs).
- Use `--log-file` to specify a custom log file (logs default to a temporary file if not specified).

For more options, run:

```bash
convoviz --help
```

### 4. Check the Output 🎉

And that's it! After running the script, head over to the output folder to see your neatly formatted Markdown files and visualizations.

![wordcloud example](demo/wordcloud-example.png)

## Share Your Feedback! 💌

I hope you find this tool useful. I'm continuously looking to improve on this, but I need your help for that.

Whether you're a tech wizard or you're new to all this, I'd love to hear about your journey with the tool. Found a quirk? Have a suggestion? Or just want to send some good vibes? I'm all ears! (see [issues](https://github.com/mohamed-chs/convoviz/issues))

And if you've had a great experience, consider giving the project a star ⭐. It keeps me motivated and helps others discover it!

## Notes

This is just a small thing I coded to help me see my convos in beautiful markdown. It was originally built with [Obsidian](https://obsidian.md/) (my go-to note-taking app) in mind, but the default output is standard Markdown.

I wasn't a fan of the clunky, and sometimes paid, browser extensions.

It was also a great opportunity to learn more about Python and type annotations. I had mypy, pyright, and ruff all on strict mode, 'twas fun.

It should(?) also work as library, so you can import and use the models and functions. I need to add more documentation for that tho. Feel free to reach out if you need help.

### Offline / reproducible runs

Word clouds use NLTK stopwords. If you're offline and NLTK data isn't installed yet, pre-download it:

```bash
python -c "import nltk; nltk.download('stopwords')"
```

### Bookmarklet

There's also a JavaScript bookmarklet flow under `js/` (experimental) for exporting additional conversation data outside the official ZIP export.
