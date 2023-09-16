## ChatGPT History to Markdown Converter 🚀

Welcome to the ChatGPT-Conversations to Markdown converter! This Python script helps you to convert conversations extracted from ChatGPT into neatly formatted Markdown (MD) files. Follow the steps below to get started! 😄

Supports **Code interpreter** output.

#### Step 1: Setting Up 🛠

<img src="images/python-logo.png" alt="Python Logo" width="70"/>

You need to have Python 'snek 🐍' installed on your system. You can download it from the [official Python website](https://www.python.org/).

#### Step 2: Clone the Repository 📥

To get the script, you'll want to clone this GitHub repository to your local system. Open a terminal or command prompt and run the following command:

```bash
git clone https://github.com/Mohamed-CHS/ChatGPT-history-export-to-Markdown.git
```

#### Step 3: Navigate to the Project Directory 📂

Next, navigate to the project directory by using the following command in your terminal or command prompt:

```bash
cd ChatGPT-history-export-to-Markdown
```

#### Step 4: Organize Your Conversations 🗂

Before you run the script, make sure your ChatGPT conversations are in a ZIP file format.

<img src="images/chatgpt-logo.png" alt="ChatGPT Logo" width="60"/>

[Learn how to export your ChatGPT history and data here](https://help.openai.com/en/articles/7260999-how-do-i-export-my-chatgpt-history-and-data).

The script will automatically find the most recent ZIP file in your 'Downloads' directory (in ~/Downloads/), but you can specify a different file or location if necessary.

#### Step 5: Running the Script 🏃‍♂️

In the terminal or command prompt, run the script with this command:

```bash
python main.py
```

The default output location for the Markdown files is : `~/Documents/ChatGPT-Conversations/MD/`. The script will automatically create the directories if they didn't exist. (which is probably the case)

#### Optional: Customize Script Inputs 🌟

Feel free to customize the script's behavior using additional parameters:

- `--out_folder`: Specify the output folder where the MD files will be saved.
- `--zip_file`: Specify the ZIP file containing the ChatGPT conversations to be converted.

Here is an example command:

```bash
python main.py --out_folder "Obsidian_Vault/Chats" --zip_file "My downloads/my_chat.zip"
```

This will extract and look for the `conversations.json` file in `~/My downloads/my_chat.zip`, and create the MD files in `~/Obsidian_Vault/Chats`.

(on **Windows**, '~/' refers to 'C:/Users/{your_username}/').

#### Step 6: Check the Output 🎉

After running the script, check the output folder for your neatly formatted Markdown files.

#### Issues and contributions 🆘

Feel free to fork this repository and make your enhancements or improvements, it still leaves a lot to be desired.

If you encounter any issues or have questions, feel free to open a discussion [here](https://github.com/Mohamed-CHS/ChatGPT-history-export-to-Markdown/issues) or in the Reddit post [here](https://www.reddit.com/r/ChatGPT/comments/16k1ub5/i_made_a_simple_chatgpt_history_to_markdown/).

#### Enjoy Your Conversations in Markdown! 🎈

I hope you find this tool useful for enjoying your ChatGPT conversations in a new, neat, and organized format!

#### Notes

This is just a small thing I coded to help me see my convos in beautiful markdown, in Obsidian (my note-taking app).

I wasn't a fan of the clunky, and sometimes paid, chrome extensions.

I'm working on automating it to add new conversations and updating old ones. Had some luck with a JavaScript bookmarklet, still ironing it out tho. Shouldn't take long.

Side note, if you'd like your math to render beautifully on Obsidian (or another markdown previewer that supports MathJax), you should replace the Latex delimiters chatgpt usually uses : `\(...\)` and `\[...\]`, with dollar sign ones : `$...$` and `$$...$$`. Note that this is **irreversible** tho, and it may not work consistently, depending on the implementation.
