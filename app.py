from __future__ import annotations

import sqlite3
from pathlib import Path

from flask import Flask, g, redirect, render_template, request, url_for, flash

APP_DIR = Path(__file__).resolve().parent
DB_PATH = APP_DIR / "drp14_2026.db"
SCHEMA_PATH = APP_DIR / "schema.sql"

app = Flask(__name__)
app.config["SECRET_KEY"] = "drp14_2026_secret_key"


# -----------------------------
# Banco de dados (SQLite)
# -----------------------------
def get_db() -> sqlite3.Connection:
    """Abre conexão SQLite e guarda no contexto da request (g)."""
    if "db" not in g:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        g.db = conn
    return g.db


@app.teardown_appcontext
def close_db(exception: Exception | None) -> None:
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db() -> None:
    db = sqlite3.connect(DB_PATH)
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        db.executescript(f.read())
    db.commit()
    db.close()


def ensure_db() -> None:
    if not DB_PATH.exists():
        init_db()


# -----------------------------
# Rotas (CRUD)
# -----------------------------
@app.get("/")
def index():
    ensure_db()
    db = get_db()

    status = request.args.get("status", "").strip()

    if status:
        rows = db.execute(
            "SELECT * FROM chamados WHERE status = ? ORDER BY id DESC",
            (status,),
        ).fetchall()
    else:
        rows = db.execute(
            "SELECT * FROM chamados ORDER BY id DESC"
        ).fetchall()

    return render_template("index.html", chamados=rows, status=status)


@app.get("/novo")
def novo():
    return render_template(
        "form.html",
        modo="criar",
        chamado={
            "titulo": "",
            "descricao": "",
            "status": "Pendente",
            "prioridade": "Média",
        },
    )


@app.post("/criar")
def criar():
    ensure_db()

    titulo = request.form.get("titulo", "").strip()
    descricao = request.form.get("descricao", "").strip()
    status = request.form.get("status", "Pendente").strip()
    prioridade = request.form.get("prioridade", "Média").strip()

    if not titulo or not descricao:
        flash("Cliente e detalhes do pedido são obrigatórios.", "error")
        return redirect(url_for("novo"))

    db = get_db()
    db.execute(
        "INSERT INTO chamados (titulo, descricao, status, prioridade) VALUES (?, ?, ?, ?)",
        (titulo, descricao, status, prioridade),
    )
    db.commit()

    flash("Pedido criado com sucesso!", "ok")
    return redirect(url_for("index"))


@app.get("/chamado/<int:chamado_id>")
def ver(chamado_id: int):
    ensure_db()
    db = get_db()
    row = db.execute(
        "SELECT * FROM chamados WHERE id = ?",
        (chamado_id,)
    ).fetchone()

    if row is None:
        flash("Pedido não encontrado.", "error")
        return redirect(url_for("index"))

    return render_template("view.html", chamado=row)


@app.get("/editar/<int:chamado_id>")
def editar(chamado_id: int):
    ensure_db()
    db = get_db()
    row = db.execute(
        "SELECT * FROM chamados WHERE id = ?",
        (chamado_id,)
    ).fetchone()

    if row is None:
        flash("Pedido não encontrado.", "error")
        return redirect(url_for("index"))

    return render_template("form.html", modo="editar", chamado=row)


@app.post("/atualizar/<int:chamado_id>")
def atualizar(chamado_id: int):
    ensure_db()

    titulo = request.form.get("titulo", "").strip()
    descricao = request.form.get("descricao", "").strip()
    status = request.form.get("status", "Pendente").strip()
    prioridade = request.form.get("prioridade", "Média").strip()

    if not titulo or not descricao:
        flash("Cliente e detalhes do pedido são obrigatórios.", "error")
        return redirect(url_for("editar", chamado_id=chamado_id))

    db = get_db()
    db.execute(
        "UPDATE chamados SET titulo = ?, descricao = ?, status = ?, prioridade = ? WHERE id = ?",
        (titulo, descricao, status, prioridade, chamado_id),
    )
    db.commit()

    flash("Pedido atualizado com sucesso!", "ok")
    return redirect(url_for("ver", chamado_id=chamado_id))


@app.post("/excluir/<int:chamado_id>")
def excluir(chamado_id: int):
    ensure_db()
    db = get_db()
    db.execute("DELETE FROM chamados WHERE id = ?", (chamado_id,))
    db.commit()

    flash("Pedido excluído.", "ok")
    return redirect(url_for("index"))


@app.get("/health")
def health():
    return {
        "status": "ok",
        "project": "Sistema de Gestão de Pedidos - DRP14_2026"
    }


if __name__ == "__main__":
    ensure_db()
    app.run(debug=True)