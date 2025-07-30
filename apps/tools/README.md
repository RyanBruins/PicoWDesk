# README.md – `/apps/tools`

Drop any self-contained HTML **utility or productivity app** here and it will be included in the *Tools* package:

1. **App file** – a single HTML file that runs entirely on its own.  
   *Example:* `Calc.html`

2. **Icon file** – 64 × 64 px ICO with **exactly the same base name** as the HTML file.  
   *Example:* `Calc.ico`

### Organizing into folders  
By default these apps appear loose on the dock.  
To group them under a folder (e.g., *Tools*, *Dev*, etc.):

- **Prefix the HTML file ONLY with `_FolderName_`**  
  *Example:* `_Tools_Calculator.html`  
  The icon **keeps its original name**: `Calculator.ico`

- Provide `Tools.ico` (64 × 64 px) if you want a custom icon for the folder; otherwise the generic `folder.ico` is used.

### Packaging  
`package-tools.sh` and `package-everything.sh` copy every `.html` and `.ico` found in this directory into `/deploy`.  
Add, remove or rename files here at will—then re-run the script to refresh your build.