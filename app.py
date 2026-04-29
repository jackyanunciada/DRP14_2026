import os
import sqlite3
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "drp14_2026"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, "drp14_2026.db")
SCHEMA_FILE = os.path.join(BASE_DIR, "schemas.sql")


def init_db():
    if not os.path.exists(DB_NAME):
        with sqlite3.connect(DB_NAME) as conn:
            with open(SCHEMA_FILE, "r", encoding="utf-8") as f:
                conn.executescript(f.read())


def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if "usuario_id" not in session:
            flash("Faça login para acessar.", "error")
            return redirect(url_for("login"))
        return func(*args, **kwargs)
    return wrapper


init_db()


PRODUTOS_CARDAPIO =  PRODUTOS_CARDAPIO = [
    {
        "id": 1,
        "nome": "Pão Francês",
        "preco": 1.00,
        "imagem": "https://images.unsplash.com/photo-1509440159596-0249088772ff",
        "descricao": "Unidade crocante e fresquinha."
    },
    {
        "id": 2,
        "nome": "Pão de Forma",
        "preco": 12.00,
        "imagem": "https://images.unsplash.com/photo-1608198093002-ad4e005484ec",
        "descricao": "Ideal para sanduíches."
    },
    {
        "id": 3,
        "nome": "Pão Integral",
        "preco": 14.00,
        "imagem": "https://images.unsplash.com/photo-1509440159596-0249088772ff",
        "descricao": "Opção mais saudável."
    },
    {
        "id": 4,
        "nome": "Croissant",
        "preco": 8.00,
        "imagem": "https://images.unsplash.com/photo-1555507036-ab1f4038808a",
        "descricao": "Folhado amanteigado."
    },
    {
        "id": 5,
        "nome": "Sonho",
        "preco": 9.00,
        "imagem": "https://images.unsplash.com/photo-1603532648955-039310d9ed75",
        "descricao": "Recheado e delicioso."
    },
    {
        "id": 6,
        "nome": "Cuca",
        "preco": 18.00,
        "imagem": "https://images.unsplash.com/photo-1608198093002-ad4e005484ec",
        "descricao": "Doce tradicional."
    }
]


def calcular_taxa_entrega(tipo_entrega: str) -> float:
    taxas = {
        "Retirada": 0.0,
        "Motoboy": 8.0,
        "Uber Entrega": 12.0
    }
    return taxas.get(tipo_entrega, 0.0)


# 🔔 FUNÇÃO DE NOTIFICAÇÕES
def get_notificacoes(usuario_id):
    conn = get_connection()

    notificacoes = conn.execute("""
        SELECT * FROM notificacoes
        WHERE usuario_id = ?
        ORDER BY criada_em DESC
        LIMIT 5
    """, (usuario_id,)).fetchall()

    nao_lidas = conn.execute("""
        SELECT COUNT(*) as total
        FROM notificacoes
        WHERE usuario_id = ? AND lida = 0
    """, (usuario_id,)).fetchone()["total"]

    conn.close()

    return notificacoes, nao_lidas


# 🔔 INJETAR NOTIFICAÇÕES NO TEMPLATE
@app.context_processor
def inject_notificacoes():
    if "usuario_id" in session:
        notificacoes, nao_lidas = get_notificacoes(session["usuario_id"])
        return dict(notificacoes=notificacoes, nao_lidas=nao_lidas)
    return dict(notificacoes=[], nao_lidas=0)


@app.route("/")
@login_required
def index():
    status = request.args.get("status", "")
    conn = get_connection()

    if status:
        pedidos = conn.execute(
            """
            SELECT * FROM pedidos
            WHERE usuario_id = ? AND status = ?
            ORDER BY id DESC
            """,
            (session["usuario_id"], status)
        ).fetchall()
    else:
        pedidos = conn.execute(
            """
            SELECT * FROM pedidos
            WHERE usuario_id = ?
            ORDER BY id DESC
            """,
            (session["usuario_id"],)
        ).fetchall()

    conn.close()
    return render_template("index.html", pedidos=pedidos, status=status)


@app.route("/cardapio")
def cardapio():
    return render_template("cardapio.html", produtos=PRODUTOS_CARDAPIO)


@app.route("/home")
def home():
    return render_template("home.html")


@app.route("/novo")
@login_required
def novo():
    item_selecionado = request.args.get("item")
    pedido = {
        "id": "",
        "cliente": session.get("usuario_nome", ""),
        "descricao": "",
        "quantidade_variedade": "",
        "status": "Pendente",
        "tipo_entrega": "Retirada",
        "taxa_entrega": 0,
        "valor_total": 0,
        "prioridade": "Média"
    }
    return render_template(
        "form.html",
        modo="criar",
        pedido=pedido,
        produtos=PRODUTOS_CARDAPIO
    )


@app.route("/criar", methods=["POST"])
@login_required
def criar():
    cliente = request.form.get("cliente") or session.get("usuario_nome", "")
    descricao = request.form.get("descricao", "").strip()
    quantidade_variedade = request.form.get("quantidade_variedade", "").strip()
    status = request.form.get("status", "Pendente")
    tipo_entrega = request.form.get("tipo_entrega", "Retirada")
    prioridade = request.form.get("prioridade", "Média")

    subtotal = float(request.form.get("subtotal", 0) or 0)
    taxa_entrega = calcular_taxa_entrega(tipo_entrega)
    valor_total = subtotal + taxa_entrega

    if not descricao or not quantidade_variedade:
        flash("Selecione pelo menos um item para criar o pedido.", "error")
        return redirect(url_for("novo"))

    conn = get_connection()
    conn.execute("""
        INSERT INTO pedidos
        (usuario_id, cliente, descricao, quantidade_variedade, status, tipo_entrega, taxa_entrega, valor_total, prioridade)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        session["usuario_id"],
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
@login_required
def ver(pedido_id):
    conn = get_connection()
    pedido = conn.execute(
        """
        SELECT * FROM pedidos
        WHERE id = ? AND usuario_id = ?
        """,
        (pedido_id, session["usuario_id"])
    ).fetchone()
    conn.close()

    if pedido is None:
        flash("Pedido não encontrado.", "error")
        return redirect(url_for("index"))

    return render_template("view.html", pedido=pedido)


@app.route("/editar/<int:pedido_id>")
@login_required
def editar(pedido_id):
    conn = get_connection()
    pedido = conn.execute(
        """
        SELECT * FROM pedidos
        WHERE id = ? AND usuario_id = ?
        """,
        (pedido_id, session["usuario_id"])
    ).fetchone()
    conn.close()

    if pedido is None:
        flash("Pedido não encontrado.", "error")
        return redirect(url_for("index"))

    return render_template(
        "form.html",
        modo="editar",
        pedido=pedido,
        produtos=PRODUTOS_CARDAPIO
    )


@app.route("/atualizar/<int:pedido_id>", methods=["POST"])
@login_required
def atualizar(pedido_id):
    cliente = request.form.get("cliente") or session.get("usuario_nome", "")
    descricao = request.form.get("descricao", "").strip()
    quantidade_variedade = request.form.get("quantidade_variedade", "").strip()
    status = request.form.get("status", "Pendente")
    tipo_entrega = request.form.get("tipo_entrega", "Retirada")
    prioridade = request.form.get("prioridade", "Média")

    subtotal = float(request.form.get("subtotal", 0) or 0)
    taxa_form = request.form.get("taxa_entrega", "")
    valor_form = request.form.get("valor_total", "")

    if taxa_form and valor_form:
        taxa_entrega = float(taxa_form)
        valor_total = float(valor_form)
    else:
        taxa_entrega = calcular_taxa_entrega(tipo_entrega)
        valor_total = subtotal + taxa_entrega

    if not descricao or not quantidade_variedade:
        flash("Preencha os dados do pedido.", "error")
        return redirect(url_for("editar", pedido_id=pedido_id))

    conn = get_connection()

    cursor = conn.execute("""
        UPDATE pedidos
        SET cliente = ?,
            descricao = ?,
            quantidade_variedade = ?,
            status = ?,
            tipo_entrega = ?,
            taxa_entrega = ?,
            valor_total = ?,
            prioridade = ?
        WHERE id = ? AND usuario_id = ?
    """, (
        cliente,
        descricao,
        quantidade_variedade,
        status,
        tipo_entrega,
        taxa_entrega,
        valor_total,
        prioridade,
        pedido_id,
        session["usuario_id"]
    ))

    # 🔔 NOTIFICAÇÃO AUTOMÁTICA
    mensagem = f"Seu pedido #{pedido_id} agora está: {status}"

    conn.execute("""
        INSERT INTO notificacoes (usuario_id, mensagem)
        VALUES (?, ?)
    """, (session["usuario_id"], mensagem))

    # ✅ UM ÚNICO COMMIT
    conn.commit()
    conn.close()

    if cursor.rowcount == 0:
        flash("Pedido não encontrado.", "error")
        return redirect(url_for("index"))

    flash("Pedido atualizado com sucesso!", "success")
    return redirect(url_for("index"))


@app.route("/excluir/<int:pedido_id>", methods=["POST"])
@login_required
def excluir(pedido_id):
    conn = get_connection()
    cursor = conn.execute(
        """
        DELETE FROM pedidos
        WHERE id = ? AND usuario_id = ?
        """,
        (pedido_id, session["usuario_id"])
    )
    conn.commit()
    conn.close()

    if cursor.rowcount == 0:
        flash("Pedido não encontrado.", "error")
        return redirect(url_for("index"))

    flash("Pedido excluído com sucesso!", "success")
    return redirect(url_for("index"))


# 🔥 CADASTRO ATUALIZADO
@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    if request.method == "POST":
        nome = request.form["nome"].strip()
        email = request.form["email"].strip().lower()
        senha = request.form["senha"]
        cpf = request.form["cpf"].strip()
        data_nascimento = request.form["data_nascimento"]
        endereco = request.form["endereco"].strip()

        conn = get_connection()
        usuario_existente = conn.execute(
            "SELECT * FROM usuarios WHERE email = ?",
            (email,)
        ).fetchone()

        if usuario_existente:
            conn.close()
            flash("Este e-mail já está cadastrado.", "error")
            return redirect(url_for("cadastro"))

        senha_hash = generate_password_hash(senha)

        conn.execute("""
            INSERT INTO usuarios (nome, email, senha, cpf, data_nascimento, endereco)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (nome, email, senha_hash, cpf, data_nascimento, endereco))

        conn.commit()
        conn.close()

        flash("Cadastro realizado com sucesso!", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        senha = request.form["senha"]

        conn = get_connection()
        usuario = conn.execute(
            "SELECT * FROM usuarios WHERE email = ?",
            (email,)
        ).fetchone()
        conn.close()

        if usuario and check_password_hash(usuario["senha"], senha):
            session["usuario_id"] = usuario["id"]
            session["usuario_nome"] = usuario["nome"]
            session["perfil"] = usuario["perfil"]  # 🔥 

            flash("Login realizado com sucesso!", "success")
            return redirect(url_for("index"))

        flash("E-mail ou senha inválidos.", "error")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("Você saiu da conta.", "success")
    return redirect(url_for("login"))


@app.route("/perfil", methods=["GET", "POST"])
@login_required
def perfil():
    conn = get_connection()

    if request.method == "POST":
        nome = request.form["nome"].strip()
        cpf = request.form["cpf"].strip()
        data_nascimento = request.form["data_nascimento"]
        endereco = request.form["endereco"].strip()

        conn.execute("""
            UPDATE usuarios
            SET nome = ?, cpf = ?, data_nascimento = ?, endereco = ?
            WHERE id = ?
        """, (nome, cpf, data_nascimento, endereco, session["usuario_id"]))

        conn.commit()

        session["usuario_nome"] = nome

        flash("Dados atualizados com sucesso!", "success")
        return redirect(url_for("perfil"))

    usuario = conn.execute(
        "SELECT * FROM usuarios WHERE id = ?",
        (session["usuario_id"],)
    ).fetchone()

    conn.close()

    return render_template("perfil.html", usuario=usuario)


def admin_required(func):  #ROTA ADMIN
    @wraps(func)
    def wrapper(*args, **kwargs):
        if "usuario_id" not in session:
            return redirect(url_for("login"))

        conn = get_connection()
        usuario = conn.execute(
            "SELECT * FROM usuarios WHERE id = ?",
            (session["usuario_id"],)
        ).fetchone()
        conn.close()

        if usuario["perfil"] != "admin":
            flash("Acesso restrito.", "error")
            return redirect(url_for("index"))

        return func(*args, **kwargs)
    return wrapper

@app.route("/admin") #ROTA ADMIN
@admin_required
def admin():
    conn = get_connection()
    pedidos = conn.execute("""
        SELECT pedidos.*, usuarios.nome
        FROM pedidos
        JOIN usuarios ON pedidos.usuario_id = usuarios.id
        ORDER BY pedidos.id DESC
    """).fetchall()
    conn.close()

    return render_template("admin.html", pedidos=pedidos)

# ATUALIZAR STATUS (ADMIN)
@app.route("/admin/atualizar/<int:pedido_id>", methods=["POST"]) 
@admin_required
def admin_atualizar(pedido_id):
    status = request.form.get("status")

    conn = get_connection()

    pedido = conn.execute(
        "SELECT * FROM pedidos WHERE id = ?",
        (pedido_id,)
    ).fetchone()

    conn.execute("""
        UPDATE pedidos
        SET status = ?
        WHERE id = ?
    """, (status, pedido_id))

    # 🔔 NOTIFICAÇÃO PARA O CLIENTE
    mensagem = f"Seu pedido #{pedido_id} foi atualizado para: {status}"

    conn.execute("""
        INSERT INTO notificacoes (usuario_id, mensagem)
        VALUES (?, ?)
    """, (pedido["usuario_id"], mensagem))

    conn.commit()
    conn.close()

    flash("Status atualizado!", "success")
    return redirect(url_for("admin"))

@app.route("/admin/pedidos")
@login_required
def admin_pedidos():
    if session.get("perfil") != "admin":
        flash("Acesso negado", "error")
        return redirect(url_for("home"))

    conn = get_connection()
    pedidos = conn.execute("SELECT * FROM pedidos ORDER BY criado_em DESC").fetchall()
    conn.close()

    return render_template("admin_pedidos.html", pedidos=pedidos)

@app.route("/admin/pedido/<int:pedido_id>/status", methods=["POST"])
@login_required
def admin_atualizar_status(pedido_id):
    if session.get("perfil") != "admin":
        flash("Acesso negado", "error")
        return redirect(url_for("home"))

    novo_status = request.form.get("status")

    conn = get_connection()
    conn.execute("UPDATE pedidos SET status=? WHERE id=?", (novo_status, pedido_id))
    conn.commit()
    conn.close()

    flash("Status atualizado!", "success")
    return redirect(url_for("admin_pedidos"))

@app.route("/faq")
def faq():
    return render_template("faq.html")



if __name__ == "__main__":
    conn = get_connection()
    conn.execute("""
        UPDATE usuarios
        SET perfil = 'admin'
        WHERE email = 'jaqueline.anunciada@gmail.com'
    """)
    conn.commit()
    conn.close()

    print("ADMIN ATUALIZADO")

    app.run(debug=True)