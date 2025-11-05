@echo off
echo Creating venv...
python -m venv .venv
call .venv\Scripts\activate
pip install -r requirements.txt
pip install pyinstaller
pyinstaller --noconsole --onefile --name PDFRenamerApp --add-data "templates;templates" --add-data "static;static" app.py
echo Build complete. See dist\PDFRenamerApp.exe (or dist\PDFRenamerApp\PDFRenamerApp.exe for one-folder build).
pause
