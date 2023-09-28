# Your entire ChatGPT data in beautiful Markdown <img src="images/markdown.png" alt="Markdown Logo" width="50"/>

## You can now try out Word Clouds 🔡☁️ on your data !

![GitHub last commit](https://img.shields.io/github/last-commit/mohamed-chs/chatgpt-history-export-to-md)
![GitHub issues](https://img.shields.io/github/issues/mohamed-chs/chatgpt-history-export-to-md)

Welcome to the ChatGPT Conversations to Markdown converter! This Python script helps you to convert your entire ChatGPT history and data export into neatly formatted Markdown files.

It adds **YAML** headers (_optional, included by default_), and also includes **Code interpreter** (Advanced Data Analysis) input / output.

<img src="images/chatgpt-logo.svg" alt="ChatGPT Logo" width="70"/>

#### See Examples : [Screenshot](demo/Fibonacci.png), [Markdown](demo/Fibonacci.md), [Markdown with dollar signs](demo/Fibonacci-dollar-signs.md), [Chat link](https://chat.openai.com/share/27b6df58-a590-41ac-9eff-f567602fe692).

## Quick setup

> See [Prerequisites](#prerequisites). (just Python and Git and you're good to go.)

### Step 1: Clone the Repository 📥

Open a terminal or command prompt and run the following command:

```bash
git clone https://github.com/mohamed-chs/chatgpt-history-export-to-md.git
```

Next, navigate to the project directory by using the following command:

```bash
cd chatgpt-history-export-to-md
```

### Step 2: Set Up the Environment 🛠️

Before running the script, you need to set up a virtual environment and install the required dependencies.

First, create a virtual environment:

```bash
python -m venv .venv
```

Activate the virtual environment:

- On **Windows**, using `cmd.exe` (*Command Prompt*):

```bash
.venv\Scripts\activate.bat
```

- On **Windows**, using *PowerShell*:

```bash
.venv\Scripts\Activate.ps1
```

- On **Linux** or **MacOS**:

```bash
source .venv/bin/activate
```

---

Now, install the necessary packages using:

```bash
pip install -r requirements.txt
```

### Step 3: Download Your Conversations data 🗂

Before you run the script, make sure your ChatGPT conversations are in a ZIP file format.

<details id="download-instructions">
  <summary>How to download : (click to expand/collapse)</summary>

<hr>
  
1.  Sign in to ChatGPT at https://chat.openai.com

2.  At the bottom of the left side bar, click on your profile name, the on **Settings**

    ![Bottom-left Widget](images/chat.openai-bottom-left-widget.png)

3.  Go to **Data controls**

    ![Settings](images/chat.openai-settings.png)

4.  In the "Data Controls" menu, click on _Export data_ : **Export**

    ![Data Controls](images/chat.openai-data-controls.png)

5.  In the confirmation modal click **Confirm export**

    ![Confirm Export](images/chat.openai-confirm-export.png)

6.  You should get an email with your data, in 2 ~ 5 minutes (check your **inbox**)

    ![Email](images/chat.openai-email.png)

7.  Click **Download data export** to download a `.zip` file containing your entire chat history and other data.

    ![ZIP File Content](images/zip-file-content.png)

    [↑ Collapse](#download-instructions)

</details>

<hr>

The script will automatically find the most recent ZIP file in your 'Downloads' directory (in `~/Downloads/`), but you can specify a different file or location if necessary.

### Step 4: Running the Script 🏃‍♂️

With the environment set up, you can now run the script. In the terminal or command prompt, execute:

```bash
python main.py
```

Now, follow the instructions on screen and choose your desired options, the script will handle the rest.

### Step 5: Check the Output 🎉

And that's it! After running the script, head over to the output folder to see your neatly formatted Markdown files.

[![Tweet](https://img.shields.io/twitter/url?style=social&url=https%3A%2F%2Fgithub.com%2Fyourusername%2Fyourrepository)](https://twitter.com/intent/tweet?text=So%2C%20this%20is%20what%20my%20entire%20ChatGPT%20history%20looks%20like%20...%0D%0A%0D%0Aby%20%40theSoCalled_%20on%20GitHub%20%3A%20http%3A%2F%2Fbit.ly%2F3ZuHCCK)

- [ ] a tweet should be fun when I later add the actual data visualizations. Feel free to implement your own data visualizations [here](src/data_visualization.py), and create a pull request, then check this box (I know you want to)

### Optional: Customize the Script's behavior 🌟

Using the `config.json`, you can modify the script's default parameters.

For example, set `"delimiters_default"` to `false` to replace all $\LaTeX$ bracket delimiters : `\(...\)` and `\[...\]`, with dollar sign ones : `$...$` and `$$...$$`, if you'd like your math to render beautifully in Markdown readers that support **MathJax** (like Obsidian).

### Acknowledgements 🌟

Big love to the following libraries that jazzed up this project!

- **[matplotlib](https://github.com/matplotlib/matplotlib)**: For making my data jump into vibrant visualizations. Art meets science, indeed! 📊

- **[nltk](https://github.com/nltk/nltk)**: Unpacking the magic of language has never been smoother. You're the NLP MVP! 📖

- **[prompt_toolkit](https://github.com/prompt-toolkit/python-prompt-toolkit)**: Command-line interfaces got a whole lot cooler with you. Kudos! 💻

- **[questionary](https://github.com/tmbo/questionary)**: For making CLI interactions fun and intuitive. Here's to engaging conversations! 💬

- **[wordcloud](https://github.com/amueller/word_cloud)**: Thanks for the visual treat with those playful word clouds. Text never looked better! ☁️

Major kudos to the developers and contributors. Your tools made this project shine! 🚀

### Issues and contributions 🆘

> See [CONTRIBUTING.md](CONTRIBUTING.md).

Feel free to fork this repository and make your enhancements or improvements. ALL contributions are welcome !

If you encounter any issues or have questions, feel free to open an [issue](https://github.com/mohamed-chs/chatgpt-history-export-to-md/issues) / [discussion](https://github.com/mohamed-chs/chatgpt-history-export-to-md/discussions).
See also : [HN post](https://news.ycombinator.com/item?id=37636701).

### Enjoy Your Conversations in Markdown! 🎈

Hopefully, you find value in this tool. If you do, giving it a star ⭐ on the repository would mean a lot. Thank you!

### Prerequisites

<img src="images/python-logo.png" alt="Python Logo" width="70" style="margin-right: 20px;"/> <img src="images/git-logo.png" alt="Git Logo" width="70"/>

Make sure you have **Python** (version >= 3.10), and **Git** installed.
You can download them from :

- [Official Python website](https://www.python.org/downloads/)
- [Official Git website](https://git-scm.com/downloads)

### Notes

This is just a small thing I coded to help me see my convos in beautiful markdown, in [Obsidian](https://obsidian.md/) (my note-taking app).

I wasn't a fan of the clunky, and sometimes paid, chrome extensions.

I'm working on automating it to add new conversations and updating old ones. Had some luck with a JavaScript bookmarklet, still ironing it out tho. Shouldn't take long.

> See [TODO](TODO.md).

> If you want the last working version with absolutely no external dependencies (no virtual environment needed), you can find it [here](https://github.com/mohamed-chs/chatgpt-history-export-to-md/tree/fe13a701fe8653c9f946b1e12979ce3bfe7104b8).
