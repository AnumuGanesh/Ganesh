# ✅ Full Flask App: Login + PDF Renamer + Compare Tabs + ZIP Download
import os
import sys
import zipfile
import uuid
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_file
from werkzeug.utils import secure_filename

def resource_path(relative_path: str) -> str:
    # Get absolute path to resource, works for dev and for PyInstaller onefile.
    try:
        base_path = sys._MEIPASS  # type: ignore[attr-defined]
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Use explicit template/static folders so PyInstaller works (onefile or onefolder)
app = Flask(__name__, template_folder=resource_path("templates"), static_folder=resource_path("static"))
app.secret_key = 'supersecretkey'

# Make runtime folders beside the executable / script working directory
RUNTIME_DIR = os.path.abspath(".")
UPLOAD_FOLDER = os.path.join(RUNTIME_DIR, 'uploads')
ZIP_FOLDER = os.path.join(RUNTIME_DIR, 'zips')
ALLOWED_EXTENSIONS = {'pdf'}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(ZIP_FOLDER, exist_ok=True)

# ------------------------
# Login (Multi-user support)
# ------------------------
users = {
    'admin@123': '1234',
    'manager@abc': 'abcd',
    'user@xyz': 'xyz123'
}

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username in users and users[username] == password:
            session['logged_in'] = True
            session['username'] = username
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error="❌ Invalid credentials")

    return render_template('login.html')

# ------------------------
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# ------------------------
@app.route('/')
def index():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('index.html', username=session.get('username'))

# ------------------------
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/rename-pdfs', methods=['POST'])
def rename_uploaded_pdfs():
    if not session.get('logged_in'):
        return jsonify({"error": "Unauthorized"}), 401
    try:
        files = request.files.getlist('files[]')
        if not files:
            return jsonify({"error": "No files uploaded"}), 400

        temp_folder = os.path.join(UPLOAD_FOLDER, str(uuid.uuid4()))
        os.makedirs(temp_folder, exist_ok=True)

        output = []
        renamed_files = []

        for file in files:
            filename = file.filename
            if file and allowed_file(filename):
                if "_SLDDRW_" in filename:
                    base = filename.split("_SLDDRW_")[0]
                    new_filename = secure_filename(base + ".pdf")
                    full_path = os.path.join(temp_folder, new_filename)
                    file.save(full_path)
                    renamed_files.append(full_path)
                    output.append(f"✅ {filename} → {new_filename}")
                else:
                    output.append(f"⚠️ Skipped: {filename} (missing _SLDDRW_)")
            else:
                output.append(f"❌ Invalid file: {filename}")

        if not renamed_files:
            return jsonify({"output": "\n".join(output), "download": None})

        zip_filename = f"renamed_{uuid.uuid4().hex}.zip"
        zip_path = os.path.join(ZIP_FOLDER, zip_filename)

        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for file_path in renamed_files:
                arcname = os.path.basename(file_path)
                zipf.write(file_path, arcname)

        return jsonify({
            "output": "\n".join(output),
            "download": url_for('download_zip', filename=zip_filename)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ------------------------
@app.route('/download/<filename>')
def download_zip(filename):
    zip_path = os.path.join(ZIP_FOLDER, filename)
    if os.path.exists(zip_path):
        return send_file(zip_path, as_attachment=True)
    return "File not found", 404

# ------------------------
@app.route('/get-folder-contents', methods=['POST'])
def get_folder_contents():
    if not session.get('logged_in'):
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json(silent=True) or {}
    folder_path = data.get("folderPath")

    if not folder_path or not os.path.exists(folder_path):
        return jsonify({"error": "Folder not found"}), 404

    try:
        all_files = os.listdir(folder_path)
        pdf_files = [f for f in all_files if f.lower().endswith('.pdf')]
        slddrw_files = [f for f in pdf_files if "_SLDDRW_" in f]

        return jsonify({
            "total_files": len(all_files),
            "pdf_files": len(pdf_files),
            "slddrw_files": len(slddrw_files),
            "sample_files": slddrw_files[:5]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Use port 5001 to avoid conflicts
    app.run(host='0.0.0.0', port=5001, debug=True)
