# PDF Renamer & Comparator (Flask)

This package contains a ready-to-run Flask web app with HTML GUI. You can run it directly with Python or build a standalone **Windows EXE**.

## Run (no EXE)
1. Install Python 3.10+
2. Open Command Prompt in this folder.
3. Create a venv (recommended):
   ```bat
   python -m venv .venv
   .venv\Scripts\activate
   ```
4. Install dependencies:
   ```bat
   pip install -r requirements.txt
   ```
5. Start the server:
   ```bat
   python app.py
   ```
6. Open http://127.0.0.1:5001 in your browser. Login with:
   - `admin@123` / `1234` (or the other seeded users in `app.py`)

## Build Windows EXE (PyInstaller)
1. In the same venv:
   ```bat
   pip install pyinstaller
   ```
2. Build **one-folder** EXE (simpler, recommended):
   ```bat
   pyinstaller --noconsole --name PDFRenamerApp ^
     --add-data "templates;templates" ^
     --add-data "static;static" ^
     app.py
   ```
   Output will be in `dist\PDFRenamerApp\`. Run `PDFRenamerApp.exe`.

3. Build **one-file** EXE (single .exe):
   ```bat
   pyinstaller --noconsole --onefile --name PDFRenamerApp ^
     --add-data "templates;templates" ^
     --add-data "static;static" ^
     app.py
   ```
   The app resolves `templates`/`static` via `sys._MEIPASS`, so one-file works too.

> EXE will create `uploads` and `zips` folders next to where you run it.

## Notes
- If port **5001** is in use, edit `app.py` and change the port.
- For LAN access, run and open `http://<your-ip>:5001` on other PCs in the same network.
- All UI is in `templates/` and `static/` (HTML/CSS). Modify freely.
