import sys
from pathlib import Path

from flask import Flask, render_template, request, jsonify


# ---------------------------------------------------------
# Project root
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ---------------------------------------------------------
# Agent
# ---------------------------------------------------------

from app.agent import answer_question, reset_memory


# ---------------------------------------------------------
# Flask application
# ---------------------------------------------------------

web_app = Flask(__name__)


# ---------------------------------------------------------
# Home page
# ---------------------------------------------------------

@web_app.route("/")
def index():
    return render_template("index.html")


# ---------------------------------------------------------
# Ask the AI agent
# ---------------------------------------------------------

@web_app.route("/ask", methods=["POST"])
def ask():

    data = request.get_json(silent=True) or {}

    question = data.get("question", "").strip()

    if not question:
        return jsonify({
            "error": "Please enter a question."
        }), 400

    try:
        result = answer_question(question)

        return jsonify(result)

    except Exception as e:

        print(f"Agent error: {e}")

        return jsonify({
            "error": "Something went wrong while processing your question."
        }), 500


# ---------------------------------------------------------
# Reset conversation
# ---------------------------------------------------------

@web_app.route("/reset", methods=["POST"])
def reset():

    try:
        reset_memory()

        return jsonify({
            "success": True
        })

    except Exception as e:

        print(f"Reset error: {e}")

        return jsonify({
            "error": "Unable to reset conversation."
        }), 500


# ---------------------------------------------------------
# Run application
# ---------------------------------------------------------

if __name__ == "__main__":

    web_app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )