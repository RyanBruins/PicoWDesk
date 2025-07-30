# README.md – `/apps/games`

Drop any self-contained HTML game here and it will automatically appear in the *Games* package:

1. **Game file** –  Self-contained HTML file with HTML/CSS/JavaScript game (no external JS/CSS).  
   *Example:* `Brickout.html`

2. **Icon file** – 64 × 64 px ICO with **exactly the same base name** as the HTML file, will automatically be used as the app icon for the HTML app with the same name.  
   *Example:* `Brickout.ico`

### Folder grouping  
To collect games under the *Games* folder instead of listing them loose on the dock:

- **Prefix the HTML file ONLY with `_Games_`**  
  *Example:* `_Games_Brickout.html`  
  The icon **keeps its original name**: `Brickout.ico`

- The desktop will create a *Games* folder icon (using `Games.ico` if present, or the generic `folder.ico` if `Games.ico` is missing).

### Packaging  
`package-games.sh` and `package-everything.sh` copy every `.html` and `.ico` found in this directory into `/deploy`.  
Edit, add or delete files here at will—then re-run the script to refresh your build.