from flask import Flask, request
import requests

app = Flask(__name__)

notes = {
    1: {"user_id": 1, "text": "Заметка пользователя 1"},
    2: {"user_id": 2, "text": "Заметка пользователя 2"},
}


def get_current_user_id():
    # Для учебной демонстрации считаем, что текущий пользователь всегда user_id=1.
    return 1


@app.route("/hello")
def hello():
    name = request.args.get("name", "Гость")
    return f"<h1>Привет, {name}!</h1>"


@app.route("/notes/<int:note_id>")
def get_note(note_id):
    note = notes.get(note_id)
    if not note:
        return "Не найдено", 404
    return note["text"]


@app.route("/fetch")
def fetch():
    url = request.args.get("url")
    if not url:
        return "Нужен параметр url", 400
    resp = requests.get(url, timeout=3)
    return resp.text