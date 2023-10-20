# Contributing Guide

Hello and welcome! 🚀

Thank you for considering a contribution to this project. Your effort, whether it's fixing bugs, adding features, or improving documentation, is deeply valued.

## First Time Contributing?

If you're new here, fret not. The codebase is well-documented, guiding you step-by-step.

## Contribution Workflow

1. **Fork the Repository**

   Start by forking the repository to your account.

2. **Clone Your Fork**

   ```bash
   git clone https://github.com/YOUR_USERNAME/chatgpt-history-export-to-md.git
   ```

3. **Create a New Branch**

   Navigate to the cloned directory and initiate a new branch:

   ```bash
   cd chatgpt-history-export-to-md
   git checkout -b your-branch-name
   ```

## Setting Up Your Development Environment

1. **Set Up a Virtual Environment with `venv`**

   It's advisable to use a virtual environment for an isolated setup:

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows, use `.venv\Scripts\activate`
   ```

2. **Install Development Dependencies**

   With your virtual environment activated:

   ```bash
   pip install -r requirements-dev.txt
   ```

3. **Development Workflow**

   - **Format the code**:

     ```bash
     ruff format .
     ```

   - **Lint the code**:

     ```bash
     ruff check .
     ```

   - **Type checks**:

     ```bash
     mypy --install-types
     mypy .
     ```

   - **Run tests**:

     ```bash
     python -m pytest
     ```

4. **Additional testing**

   You can also check [notebook](playground.ipynb) to see how the output looks.

## Committing and Pushing Changes

1. **Commit Your Changes**

   ```bash
   git commit -m "Descriptive message about your changes"
   ```

2. **Push Your Branch**

   ```bash
   git push origin your-branch-name
   ```

3. **Open a Pull Request (PR)**

   Navigate to the main repository and initiate a PR. Including demos or screenshots will enrich the review process.

**Note**: Before pushing your changes, ensure that you reset the `user_config.json` file to its original state. (unless you want to add or change the default values)

## Seeking Contribution Ideas?

- Peruse the `Issues` tab for open bugs or feature suggestions.
- Explore the [Project Todo](TODO.md) and [JavaScript Todo](js/how_to_use.md#still-working-on).
- Get a project overview from [here](assets/deps_graph.png). Generated using :

  ```bash
  pydeps cli.py -o assets/deps_graph.png -T png --noshow --reverse --rankdir BT --exclude-exact models views controllers utils
  ```

## Documentation Insights

Engage with the codebase; in-code comments and docstrings offer ample context.

## In Closing

Every contribution, big or small, enriches the project. We eagerly await your additions!

Catch you in the PRs! 🚀
