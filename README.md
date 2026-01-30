<p align="center">
  <h1 align="center">Convoviz 📊</h1>
  <p align="center"><strong>Visualize your entire ChatGPT data</strong></p>
  <p align="center">
    Convert your ChatGPT history into well-formatted Markdown files.<br>
    Visualize your data with word clouds 🔡☁️ and usage graphs 📈.
  </p>
</p>

<p align="center">
  <a href="https://pypi.org/project/convoviz/"><img src="https://img.shields.io/pypi/v/convoviz?style=for-the-badge&logo=python&logoColor=white" alt="PyPI Version"></a>
  <a href="https://github.com/mohamed-chs/convoviz/blob/main/LICENSE"><img src="https://img.shields.io/pypi/l/convoviz?style=for-the-badge" alt="License"></a>
  <a href="https://pepy.tech/projects/convoviz"><img src="https://img.shields.io/pepy/dt/convoviz?style=for-the-badge&color=blue" alt="Downloads"></a>
  <a href="https://github.com/mohamed-chs/convoviz/actions/workflows/ci.yml"><img src="https://img.shields.io/github/actions/workflow/status/mohamed-chs/convoviz/ci.yml?style=for-the-badge&logo=github&label=CI" alt="CI Status"></a>
</p>

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 📝 **Markdown Export** | Clean, well-formatted Markdown with optional YAML headers |
| 🖼️ **Inline Images** | Media attachments rendered directly in your Markdown files |
| ☁️ **Word Clouds** | Visual breakdowns of your most-used words and phrases |
| 📈 **Usage Graphs** | Bar plots and charts showing your conversation patterns |

> 💡 **See examples in the [`demo/`](https://github.com/mohamed-chs/convoviz/tree/main/demo) folder!**

---

## 📖 How to Use

### Step 1: Export Your ChatGPT Data

1. Sign in at [chatgpt.com](https://chatgpt.com)
2. Navigate to: **Profile Name** (bottom left) → **Settings** → **Data controls** → **Export**
3. Click **Confirm export**
4. Wait for the email from OpenAI, then download the `.zip` file

---

### Step 2: Install Convoviz

<details open>
<summary><strong>🚀 Quick Install (Recommended)</strong></summary>

One command installs everything you need — [uv](https://github.com/astral-sh/uv) (a fast Python package manager) and convoviz with graphs and word clouds.

**Linux / macOS:**

```bash
curl -fsSL https://raw.githubusercontent.com/mohamed-chs/convoviz/main/install.sh | bash
```

**Windows (PowerShell):**

```powershell
irm https://raw.githubusercontent.com/mohamed-chs/convoviz/main/install.ps1 | iex
```

</details>

<details>
<summary><strong>📦 Alternative: Install with pip</strong></summary>

If you prefer using `pip` directly:

```bash
# Create a virtual environment (keeps your system Python clean)
python3 -m venv .venv

# Activate the virtual environment
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install convoviz with visualization extras
pip install "convoviz[viz]"
```

</details>

---

### Step 3: Run Convoviz

The simplest way is to run the command and follow the interactive prompts:

```bash
convoviz
```

Or, provide arguments directly to skip the prompts:

```bash
convoviz --input path/to/your/export.zip --output path/to/output/folder
```

<details>
<summary><strong>⚙️ Command Line Options</strong></summary>

#### Selective Output

By default, all outputs (Markdown, graphs, word clouds) are generated. Use `--outputs` to pick specific ones:

```bash
convoviz --input export.zip --outputs markdown --outputs graphs
```

Available options: `markdown`, `graphs`, `wordclouds`

> In interactive mode, you'll be prompted to choose which outputs to generate.

#### Other Useful Flags

| Flag | Description |
|------|-------------|
| `--zip` / `-z` | Alias for `--input` (for convenience) |
| `--no-interactive` | Force non-interactive mode |
| `--flat` | Put all Markdown files in a single folder (instead of organizing by date) |
| `--verbose` / `-v` | Enable detailed logging (use `-vv` for debug logs) |
| `--log-file PATH` | Specify a custom log file location |

For a complete list of options:

```bash
convoviz --help
```

</details>

---

### Step 4: Check the Output 🎉

After running the script, head to your output folder to see:
- 📝 Neatly formatted Markdown files
- 📊 Visualizations and graphs

![wordcloud example](https://raw.githubusercontent.com/mohamed-chs/convoviz/main/demo/wordcloud-example.png)

---

## 💌 Share Your Feedback!

I hope you find this tool useful. I'm continuously looking to improve on this, but I need your help for that.

Whether you're a tech wizard or you're new to all this, I'd love to hear about your journey with the tool. Found a quirk? Have a suggestion? Or just want to send some good vibes? I'm all ears!

👉 **[Open an Issue](https://github.com/mohamed-chs/convoviz/issues)**

And if you've had a great experience, consider giving the project a ⭐ **star**! It keeps me motivated and helps others discover it!

---

## 🤝 Contributing

Interested in contributing? Check out the **[Contributing Guide](https://github.com/mohamed-chs/convoviz/tree/main/CONTRIBUTING.md)** for development setup, code style, and how to submit a pull request.

---

## 📝 Notes

<details>
<summary><strong>About This Project</strong></summary>

This is just a small thing I coded to help me see my convos in beautiful markdown. It was originally built with [Obsidian](https://obsidian.md/) (my go-to note-taking app) in mind, but the default output is standard Markdown.

I wasn't a fan of the clunky, and sometimes paid, browser extensions.

It was also a great opportunity to learn more about Python and type annotations. I had mypy, pyright, and ruff all on strict mode, 'twas fun.

</details>

<details>
<summary><strong>Using as a Library</strong></summary>

It should also work as a library, so you can import and use the models and functions. I need to add more documentation for that though. Feel free to reach out if you need help.

</details>

<details>
<summary><strong>Offline / Reproducible Runs</strong></summary>

Word clouds use NLTK stopwords. If you're offline and NLTK data isn't installed yet, pre-download it:

```bash
python -c "import nltk; nltk.download('stopwords')"
```

</details>

<details>
<summary><strong>Bookmarklet (Experimental)</strong></summary>

There's also a JavaScript bookmarklet flow under `js/` for exporting additional conversation data outside the official ZIP export. This is experimental.

</details>
