import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = "drp14_2026"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, "drp14_2026.db")
SCHEMA_FILE = os.path.join(BASE_DIR, "schemas.sql")


def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        with open(SCHEMA_FILE, "r", encoding="utf-8") as f:
            conn.executescript(f.read())


def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


init_db()


@app.route("/")
def index():
    status = request.args.get("status", "")
    conn = get_connection()

    if status:
        pedidos = conn.execute(
            "SELECT * FROM pedidos WHERE status = ? ORDER BY id DESC",
            (status,)
        ).fetchall()
    else:
        pedidos = conn.execute(
            "SELECT * FROM pedidos ORDER BY id DESC"
        ).fetchall()

    conn.close()
    return render_template("index.html", pedidos=pedidos, status=status)


@app.route("/cardapio")
def cardapio():
    return render_template("cardapio.html")


@app.route("/novo")
def novo():
    pedido = {
        "id": "",
        "cliente": "",
        "descricao": "",
        "quantidade_variedade": "",
        "status": "Pendente",
        "tipo_entrega": "Retirada",
        "taxa_entrega": 0,
        "valor_total": 0,
        "prioridade": "Média"
    }
    return render_template("form.html", modo="criar", pedido=pedido)


@app.route("/criar", methods=["POST"])
def criar():
    cliente = request.form["cliente"]
    descricao = request.form["descricao"]
    quantidade_variedade = request.form["quantidade_variedade"]
    status = request.form["status"]
    tipo_entrega = request.form["tipo_entrega"]
    taxa_entrega = request.form["taxa_entrega"]
    valor_total = request.form["valor_total"]
    prioridade = request.form["prioridade"]

    conn = get_connection()
    conn.execute("""
        INSERT INTO pedidos
        (cliente, descricao, quantidade_variedade, status, tipo_entrega, taxa_entrega, valor_total, prioridade)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        cliente,
        descricao,
        quantidade_variedade,
        status,
        tipo_entrega,
        taxa_entrega,
        valor_total,
        prioridade
    ))
    conn.commit()
    conn.close()

    flash("Pedido criado com sucesso!", "success")
    return redirect(url_for("index"))


@app.route("/ver/<int:pedido_id>")
def ver(pedido_id):
    conn = get_connection()
    pedido = conn.execute(
        "SELECT * FROM pedidos WHERE id = ?",
        (pedido_id,)
    ).fetchone()
    conn.close()

    if pedido is None:
        flash("Pedido não encontrado.", "error")
        return redirect(url_for("index"))

    return render_template("view.html", pedido=pedido)


@app.route("/editar/<int:pedido_id>")
def editar(pedido_id):
    conn = get_connection()
    pedido = conn.execute(
        "SELECT * FROM pedidos WHERE id = ?",
        (pedido_id,)
    ).fetchone()
    conn.close()

    if pedido is None:
        flash("Pedido não encontrado.", "error")
        return redirect(url_for("index"))

    return render_template("form.html", modo="editar", pedido=pedido)


@app.route("/atualizar/<int:pedido_id>", methods=["POST"])
def atualizar(pedido_id):
    cliente = request.form["cliente"]
    descricao = request.form["descricao"]
    quantidade_variedade = request.form["quantidade_variedade"]
    status = request.form["status"]
    tipo_entrega = request.form["tipo_entrega"]
    taxa_entrega = request.form["taxa_entrega"]
    valor_total = request.form["valor_total"]
    prioridade = request.form["prioridade"]

    conn = get_connection()
    conn.execute("""
        UPDATE pedidos
        SET cliente = ?,
            descricao = ?,
            quantidade_variedade = ?,
            status = ?,
            tipo_entrega = ?,
            taxa_entrega = ?,
            valor_total = ?,
            prioridade = ?
        WHERE id = ?
    """, (
        cliente,
        descricao,
        quantidade_variedade,
        status,
        tipo_entrega,
        taxa_entrega,
        valor_total,
        prioridade,
        pedido_id
    ))
    conn.commit()
    conn.close()

    flash("Pedido atualizado com sucesso!", "success")
    return redirect(url_for("index"))


@app.route("/excluir/<int:pedido_id>", methods=["POST"])
def excluir(pedido_id):
    conn = get_connection()
    conn.execute("DELETE FROM pedidos WHERE id = ?", (pedido_id,))
    conn.commit()
    conn.close()

    flash("Pedido excluído com sucesso!", "success")
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)