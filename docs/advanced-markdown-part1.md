### 1. Callouts & Admonitions (Deep Dive)

While standard blockquotes (`> text`) are useful, Callouts transform them into colorful, icon-labeled alert boxes.

#### A. The Universal Syntax
Both GitHub and Obsidian use a specific "block quote variation" syntax. It must start with a blockquote `>` immediately followed by `[!TYPE]`.

```markdown
> [!NOTE]
> This is the content of the note.
> It can span multiple lines.
```

#### B. The "Standard 5" (GitHub & Obsidian Compatible)
GitHub is stricter than Obsidian. To ensure your notes look good on **both** platforms, stick to these five types. GitHub refers to these as "Alerts."

| Type | Color | Icon | Usage |
| :--- | :--- | :--- | :--- |
| `[!NOTE]` | Blue 🔵 | ℹ️ | General information / FYI. |
| `[!TIP]` | Green 🟢 | 💡 | Advice or optimizations. |
| `[!IMPORTANT]` | Purple 🟣 | 💬 | Key information users shouldn't miss. |
| `[!WARNING]` | Yellow 🟡 | ⚠️ | Warnings about potential issues. |
| `[!CAUTION]` | Red 🔴 | 🛑 | Dangerous actions (e.g., deleting data). |

#### C. Obsidian-Specific Superpowers
Obsidian's implementation is much more robust than GitHub's.

**1. Foldable Callouts**
You can make callouts collapsible (like an accordion) directly in the syntax.
*   `> [!NOTE]-` (Minus sign): Defaults to **closed** (collapsed).
*   `> [!NOTE]+` (Plus sign): Defaults to **open** (expanded).

```markdown
> [!FAQ]- Can I fold this?
> Yes! This content is hidden until you click the header.
```

**2. Custom Titles**
You don't have to use the Type name as the Title.
```markdown
> [!WARNING] Don't Press the Button!
> You can write whatever you want in the header.
```

**3. Extended Types (Obsidian Only)**
Obsidian supports many more types out of the box. *Note: On GitHub, these will simply render as a standard blockquote.*
*   `[!TODO]` (Blue)
*   `[!EXAMPLE]` (Purple)
*   `[!QUOTE]` (Grey/Cited style)
*   `[!BUG]` (Red)
*   `[!SUCCESS]` (Green)
*   `[!QUESTION]` (Orange)

**4. Nested Callouts**
You can put a callout inside a callout by adding an extra `>`.
```markdown
> [!NOTE] Main Note
> Here is some info.
>
>> [!TIP] Pro Tip
>> This is a tip inside the note!
```

---

### 2. Collapsible Sections (`<details>` HTML)

This feature is not actually Markdown; it is raw HTML5. Because Markdown supports HTML, this works beautifully in GitHub `README.md` files, PR comments, and Obsidian notes.

#### A. Basic Syntax
You need three parts:
1.  `<details>`: The container.
2.  `<summary>`: The clickable text (the arrow points to this).
3.  The content.

```html
<details>
<summary>Click to reveal the answer</summary>

The answer is 42.

</details>
```

#### B. The "Blank Line" Rule (Crucial)
If you want to use **Markdown formatting** (bold, lists, code blocks) *inside* the hidden section, you **must** leave a blank line after the closing `</summary>` tag and before the closing `</details>` tag.

**Incorrect (Markdown won't render):**
```html
<details><summary>My Code</summary>
```python
print("Fail")
```
</details>
```

**Correct (Markdown renders):**
```html
<details>
<summary>My Code</summary>

```python
print("Success")
```

</details>
```

#### C. Styling the Summary
The `<summary>` tag behaves like a button. You can use Markdown headers inside it to make it larger.

```html
<details>
<summary>

### 🚨 Click for Error Logs

</summary>

Error: System failure at line 42.

</details>
```

---

### 3. Combining Them (Advanced Layouts)

You can mix these features for sophisticated documentation layouts.

#### Use Case 1: The "Spoiler" List
A list of items where the description is hidden to keep the interface clean.

```markdown
1. **Step One:** Install Software
2. **Step Two:** Configure Settings
    <details>
    <summary>View Configuration details</summary>

    > [!TIP]
    > Make sure to set `debug=true` during setup.

    </details>
3. **Step Three:** Run
```

#### Use Case 2: The "Mega-Warning" (GitHub specific)
GitHub often uses this pattern in Release Notes to hide a long list of breaking changes inside a warning box.

```markdown
> [!WARNING] Breaking Changes in v2.0
> We have removed legacy support.
>
> <details>
> <summary>Click to view the full list of deprecated endpoints</summary>
>
> 1. `/api/v1/auth`
> 2. `/api/v1/login`
>
> </details>
```

### Summary of Platform Differences

| Feature | GitHub | Obsidian |
| :--- | :--- | :--- |
| **Syntax** | `> [!TYPE]` | `> [!TYPE]` |
| **Colors** | Fixed (5 types) | Customizable via CSS |
| **Icons** | SVG (Fixed) | Customizable via CSS |
| **Collapsible Callouts** | ❌ No (Must use `<details>`) | ✅ Yes (`[!TYPE]-`) |
| **Foldable HTML** | ✅ `<details>` works | ✅ `<details>` works |
| **Rendering Non-standard types** | Renders as plain text quote | Renders with default gray icon |