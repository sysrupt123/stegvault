import io
from flask import Flask, render_template, request, send_file
from cryptography.fernet import InvalidToken
from stego import hide, reveal

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # reject uploads over 5 MB


@app.errorhandler(413)
def too_large(e):
    return render_template("index.html", error="File too large (max 5 MB)."), 413


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/hide", methods=["POST"])
def hide_route():
    file = request.files.get("image")
    message = request.form.get("message", "")
    password = request.form.get("password", "")
    if not file or not message or not password:
        return render_template("index.html", error="Fill in all fields.")
    try:
        out = io.BytesIO()
        hide(io.BytesIO(file.read()), out, message, password)
        out.seek(0)
        return send_file(out, mimetype="image/png",
                         as_attachment=True, download_name="secret.png")
    except ValueError as e:
        return render_template("index.html", error=str(e))
    except Exception:
        return render_template("index.html",
                               error="Could not process that image. Try a PNG or JPG.")


@app.route("/reveal", methods=["POST"])
def reveal_route():
    file = request.files.get("image")
    password = request.form.get("password", "")
    if not file or not password:
        return render_template("index.html", error="Fill in all fields.")
    try:
        text = reveal(io.BytesIO(file.read()), password)
        return render_template("index.html", result=text)
    except (InvalidToken, ValueError):
        # same message for both cases, so it doesn't leak which one failed
        return render_template("index.html",
                               error="Wrong password, or no hidden message in this image.")
    except Exception:
        return render_template("index.html", error="Could not process that image.")


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
