## ChatGPT History to Markdown Converter 🚀

Welcome to the ChatGPT-Conversations to Markdown converter! This Python script helps you to convert conversations extracted from ChatGPT into neatly formatted Markdown (MD) files. Follow the steps below to get started! 😄

Supports **Code interpreter** output.

#### Step 1: Setting Up 🛠

<img src="images/python-logo.png" alt="Python Logo" width="70"/>

You need to have Python 'snek 🐍' installed on your system. You can download it from the [official Python website](https://www.python.org/).

#### Step 2: Get the Script 📥

You have two options here - you can either download the ZIP file or clone the GitHub repository.

##### Option A: Download the ZIP

Click the green 'Code' button near the top right corner and choose the 'Download ZIP' option. Once downloaded, extract it to a convenient location on your computer.

##### Option B: Clone the Repository (Recommended)

If you have git installed, open a terminal or command prompt and run the following command to clone the repository:

```bash
git clone https://github.com/Mohamed-CHS/ChatGPT-history-export-to-Markdown.git
```

This will create a copy of the project in your local system.

#### Step 3: Navigate to the Project Directory 📂

Open a terminal or command prompt and navigate to the directory where you cloned or extracted the files. Here is how you can do it:

```bash
cd path/to/ChatGPT-history-export-to-Markdown
```

Replace `path/to` with the actual path where the project resides.

#### Step 4: Organize Your Conversations 🗂

Before running the script, ensure that your ChatGPT conversations are in a ZIP file format.

<img src="images/chatgpt-logo.png" alt="Python Logo" width="60"/>

[This is how you can export your ChatGPT history and data](https://help.openai.com/en/articles/7260999-how-do-i-export-my-chatgpt-history-and-data).

The script is set up to automatically look for the most recent ZIP file in your 'Downloads' folder (in `~/Downloads/`), but you can specify a different file or location if necessary.

#### Step 5: Running the Script 🏃‍♂️

In the terminal or command prompt, run the script using the following command:

```bash
python main.py
```

Or alternatively, you can open the `main.py` file in any code editor and just hit "Run code".

#### Optional: Customize Script Inputs 🌟

You can customize the script's behavior using additional parameters:

- `--out_folder`: Specify the output folder where the MD files will be saved.
- `--zip_file`: Specify the ZIP file containing the ChatGPT conversations to be converted.

For example:

```bash
python main.py --out_folder "Obsidian_Vault/Chats" --zip_file "My downloads/my_chat.zip"
```

This will extract and look for the `conversations.json` file in `~/My downloads/my_chat.zip`, and create the MD files in `~/Obsidian_Vault/Chats`.

(on **Windows**, '~/' would be 'C://Users/your_username/').

#### Step 6: Check the Output 🎉

Once the script runs successfully, check the specified output folder (or the default location) for the generated Markdown files. Each conversation will have its own file with details neatly formatted.

#### Help and Support 🆘

Feel free to open and discuss issues [here](https://github.com/Mohamed-CHS/ChatGPT-history-export-to-Markdown/issues), or in the Reddit post [here](https://www.reddit.com/r/ChatGPT/comments/16k1ub5/i_made_a_simple_chatgpt_history_to_markdown/).

#### Enjoy Your Conversations in Markdown! 🎈

We hope you find this tool useful for enjoying your ChatGPT conversations in a new, neat, and organized format!

#### Notes

This is just a small thing I coded to help me see my convos in beautiful markdown, in Obsidian (my note-taking app).

I wasn't a fan of the clunky, and sometimes paid, chrome extensions.

I'm working on automating it to add new conversations and updating old ones. Had some luck with a JavaScript bookmarklet, still ironing it out tho. Shouldn't take long.

Side note, if you'd like your math to render beautifully on Obsidian (or another markdown previewer that supports MathJax), you should replace the Latex delimiters chatgpt usually uses : `\(...\)` and `\[...\]` with dollar sign ones : `$...$` and `$$...$$`. Note that this is **irreversible** tho, and it may not work consistently, depending on the implementation.

Feel free to fork this repository and make your enhancements or improvements.
