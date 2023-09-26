# Your entire ChatGPT data in beautiful Markdown <img src="images/markdown.png" alt="Markdown Logo" width="50"/>

![GitHub last commit](https://img.shields.io/github/last-commit/mohamed-chs/chatgpt-history-export-to-md)
![GitHub issues](https://img.shields.io/github/issues/mohamed-chs/chatgpt-history-export-to-md)

Welcome to the ChatGPT Conversations to Markdown converter! This Python script helps you to convert your entire ChatGPT history and data export into neatly formatted Markdown files.

It adds **YAML** headers (_optional, included by default_), and also includes **Code interpreter** (Advanced Data Analysis) input / output.

<img src="images/chatgpt-logo.svg" alt="ChatGPT Logo" width="70"/>

#### See Examples : [Screenshot](demo/Fibonacci.png), [Markdown](demo/Fibonacci.md), [Markdown with dollar signs](demo/Fibonacci-dollar-signs.md), [Chat link](https://chat.openai.com/share/27b6df58-a590-41ac-9eff-f567602fe692).

## Quick setup

> See [Prerequisites](#prerequisites). (just Python and Git and you're good to go. **No external dependencies !**)

### Step 1: Clone the Repository 📥

Open a terminal or command prompt and run the following command:

```bash
git clone https://github.com/mohamed-chs/chatgpt-history-export-to-md.git
```

Next, navigate to the project directory by using the following command:

```bash
cd chatgpt-history-export-to-md
```

### Step 2: Download Your Conversations data 🗂

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

### Step 3: Running the Script 🏃‍♂️

In the terminal or command prompt, run the script with this command:

```bash
python main.py
```

The default output location for the Markdown files is : `~/Documents/ChatGPT-Conversations/MD/`. The script will automatically create the directories if they didn't exist. Feel free to [customize](#optional-customize-the-scripts-behavior-🌟) the script's behavior.

### Step 4: Check the Output 🎉

And that's it! After running the script, check the output folder for your neatly formatted Markdown files.

[![Tweet](https://img.shields.io/twitter/url?style=social&url=https%3A%2F%2Fgithub.com%2Fyourusername%2Fyourrepository)](https://twitter.com/intent/tweet?text=So%2C%20this%20is%20what%20my%20entire%20ChatGPT%20history%20looks%20like%20...%0D%0A%0D%0Aby%20%40theSoCalled_%20on%20GitHub%20%3A%20http%3A%2F%2Fbit.ly%2F3ZuHCCK)

- [ ] a tweet should be fun when I later add the actual data visualizations. Feel free to implement your own data visualizations [here](src/data_visualization.py), and create a pull request, then check this box (I know you want to)

### Optional: Customize the Script's behavior 🌟

#### command line parameters

Feel free to customize the script's behavior using additional parameters:

- `--out_folder`: Specify the output folder where the MD files will be saved.
- `--zip_file`: Specify the ZIP file containing the ChatGPT conversations to be converted.

Here is an example command:

```bash
python main.py --out_folder "Obsidian_Vault/Chats" --zip_file "My downloads/my_chat.zip"
```

This will extract and look for the `conversations.json` file in `~/My downloads/my_chat.zip`, and create the MD files in `~/Obsidian_Vault/Chats`.

<img src="images/obsidian-logo.png" alt="Obsidian Logo" width="50"/>

(on **Windows**, `~/` refers to `C:/Users/{your_username}/`).

#### `config.json`

You can also modify the [config.json](config.json) file, to customize the output :

```json
{
  "system_title": "System",
  "user_title": "YOUR NAME",
  "assistant_title": "My AI",
  "tool_title": "Code output (or plugin name)",
  "delimiters_default": true
}
```

Change `"delimiters_default"` to `false` to replace all $\LaTeX$ bracket delimiters : `\(...\)` and `\[...\]`, with dollar sign ones : `$...$` and `$$...$$`, if you'd like your math to render beautifully in Markdown readers that support **MathJax** (like Obsidian).

You can also configure the YAML header in the `config.json` to add or remove fields.

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

Yep, no external dependencies needed.

### TODO

Doing what needs to be done.

Feel free to add or check items.

**general**

- [x] keep external dependencies to a minimum (0 so far)
- [x] Javascript to download more conversations, see [Javascript](javascript)
- [ ] Add new downloaded conversations to the MD folder
- [ ] Update past conversations if changed
- [ ] More robust testing setup
- [ ] Data visualizations : chat times, frequency, models, word clouds, etc...
- [ ] Data analysis : categories and more classifications based on topics, concepts, programming tools, etc ...
- [ ] Integration with Obsidian (folders and subfolders, tags, ...)
- [ ] Add HTML as an output option
- [ ] Format more content data, for example : plugin use
- [ ] Support different response selections in a chat
- [ ] Extract more data from the JSON files, like user feedback per message
- [ ] Option to add metadata for each individual message
- [ ] more todos ...

**command line**

- [ ] Nicer command line output formatting
- [ ] More configs from the command line (overwrite the config.json)
- [ ] Link to submit issues or feedback
- [ ] more todos ...

**configs.json**

- [x] change user, assistant, and system names
- [x] yaml header elements
- [ ] specific configs for each individual conversation / conversation type
- [ ] output folder (currently set by default or via command line arguments)
- [ ] more configs ...

> See also : [JavaScript Todo](javascript/how_to_use.md#still-working-on)

### Notes

This is just a small thing I coded to help me see my convos in beautiful markdown, in [Obsidian](https://obsidian.md/) (my note-taking app).

I wasn't a fan of the clunky, and sometimes paid, chrome extensions.

I'm working on automating it to add new conversations and updating old ones. Had some luck with a JavaScript bookmarklet, still ironing it out tho. Shouldn't take long.
