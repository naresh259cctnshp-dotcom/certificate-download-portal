import json
import os
import re
from pathlib import Path
from flask import Flask, render_template, request, send_from_directory, abort

BASE_DIR = Path(__file__).resolve().parent
CERTIFICATE_DIR = BASE_DIR / "certificates"
MAPPING_FILE = BASE_DIR / "mapping.json"

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024  # 2 MB request limit


def normalize_mobile(value):
    """Keep digits only; accept numbers entered with spaces or +91 prefix."""
    digits = re.sub(r"\D", "", value or "")
    if len(digits) == 12 and digits.startswith("91"):
        digits = digits[2:]
    return digits


def load_mapping():
    try:
        with MAPPING_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)
        return data if isinstance(data, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


@app.route("/", methods=["GET", "POST"])
def index():
    error = None
    success = False

    if request.method == "POST":
        mobile = normalize_mobile(request.form.get("mobile", ""))

        if len(mobile) != 10:
            error = "Please enter a valid 10-digit mobile number."
        else:
            mapping = load_mapping()
            filename = mapping.get(mobile)

            # Only allow a simple filename; never accept a user-supplied path.
            if not isinstance(filename, str) or Path(filename).name != filename:
                error = "No certificate was found for this mobile number. Please check the number."
            else:
                certificate_path = CERTIFICATE_DIR / filename
                if certificate_path.is_file() and certificate_path.suffix.lower() == ".pdf":
                    return send_from_directory(
                        CERTIFICATE_DIR,
                        filename,
                        as_attachment=True,
                        download_name=filename
                    )
                error = "Your certificate is not available yet. Please contact the event organiser."

    return render_template("index.html", error=error)


@app.errorhandler(413)
def request_too_large(_error):
    return "Request too large.", 413


if __name__ == "__main__":
    # Local testing only. For public hosting, use a production WSGI server.
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT", 5000)), debug=False)
