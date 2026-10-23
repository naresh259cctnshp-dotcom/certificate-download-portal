```python
import json
import os
import re
import secrets
from pathlib import Path

from flask import (
    Flask,
    render_template,
    request,
    send_from_directory,
    redirect,
    url_for,
    session,
)

BASE_DIR = Path(__file__).resolve().parent
CERTIFICATE_DIR = BASE_DIR / "certificates"
MAPPING_FILE = BASE_DIR / "mapping.json"

app = Flask(__name__)

# Render Environment Variables mein SECRET_KEY set karein.
app.secret_key = os.environ.get("SECRET_KEY") or secrets.token_hex(32)

# Session cookie settings
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024


def normalize_mobile(value):
    """Mobile number se spaces aur special characters remove karein."""
    digits = re.sub(r"\D", "", value or "")

    if len(digits) == 12 and digits.startswith("91"):
        digits = digits[2:]

    return digits


def load_mapping():
    """mapping.json se mobile number aur certificate filename read karein."""
    try:
        with MAPPING_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)

        return data if isinstance(data, dict) else {}

    except (OSError, json.JSONDecodeError):
        return {}


@app.route("/", methods=["GET", "POST"])
def index():
    error = None

    if request.method == "POST":
        mobile = normalize_mobile(request.form.get("mobile", ""))

        if len(mobile) != 10:
            error = "Please enter a valid 10-digit mobile number."

        else:
            mapping = load_mapping()
            filename = mapping.get(mobile)

            # Filename ke through folder traversal rokna
            if (
                not isinstance(filename, str)
                or Path(filename).name != filename
                or filename in ("", ".", "..")
            ):
                error = (
                    "No certificate was found for this mobile number. "
                    "Please check the number."
                )

            else:
                certificate_path = CERTIFICATE_DIR / filename

                if (
                    certificate_path.is_file()
                    and certificate_path.suffix.lower() in (".jpg", ".jpeg")
                ):
                    # Download ke liye one-time session token banayein
                    token = secrets.token_urlsafe(24)

                    session["download_token"] = token
                    session["download_file"] = filename

                    # POST ke baad redirect: refresh par POST repeat nahi hoga
                    return redirect(url_for("download_certificate", token=token))

                else:
                    error = (
                        "Certificate not found. Please check the filename "
                        "and try again."
                    )

    return render_template("index.html", error=error)


@app.route("/download/<token>")
def download_certificate(token):
    """Certificate ko ek baar download karke token invalidate karein."""

    saved_token = session.get("download_token")
    filename = session.get("download_file")

    if not saved_token or not secrets.compare_digest(token, saved_token):
        return redirect(url_for("index"))

    # Token ko download response se pehle invalidate karein
    session.pop("download_token", None)
    session.pop("download_file", None)

    if (
        not isinstance(filename, str)
        or Path(filename).name != filename
        or filename in ("", ".", "..")
    ):
        return redirect(url_for("index"))

    certificate_path = CERTIFICATE_DIR / filename

    if (
        not certificate_path.is_file()
        or certificate_path.suffix.lower() not in (".jpg", ".jpeg")
    ):
        return redirect(url_for("index"))

    return send_from_directory(
        str(CERTIFICATE_DIR),
        filename,
        as_attachment=True,
        download_name=filename,
        mimetype="image/jpeg",
        max_age=0,
    )


@app.errorhandler(413)
def request_too_large(_error):
    return "Request too large.", 413


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=False,
    )
```
