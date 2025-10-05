from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import mysql.connector
from werkzeug.security import check_password_hash, generate_password_hash

auth_bp = Blueprint('auth', __name__, template_folder='.')

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        database="delivery",
        user="root",    # padrão XAMPP
        password=""     # normalmente vazio
    )

# ------------------------
# LOGIN
# ------------------------
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get("username").strip()
        senha = request.form.get("password").strip()

        if not email or not senha:
            flash("Preencha todos os campos!", "warning")
            return redirect(url_for("auth.login"))

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, nome, senha, role FROM usuarios WHERE email = %s", (email,))
        user = cur.fetchone()
        cur.close()
        conn.close()

        if not user:
            flash("E-mail não encontrado.", "danger")
        elif not check_password_hash(user[2], senha):
            flash("Senha inválida.", "danger")
        else:
            session['user'] = {"id": user[0], "nome": user[1], "role": user[3]}
            flash(f"Bem-vindo, {user[1]}!", "success")
            return redirect(url_for("cardapio.menu"))

    return render_template("login.html", active_page="login")

# ------------------------
# REGISTRO
# ------------------------
@auth_bp.route('/register', methods=['POST'])
def register():
    nome = request.form.get("nome").strip()
    email = request.form.get("email").strip()
    senha = request.form.get("senha").strip()

    if not nome or not email or not senha:
        flash("Todos os campos são obrigatórios!", "warning")
        return redirect(url_for("auth.login"))

    conn = get_db_connection()
    cur = conn.cursor()

    # Verificar se o email já existe
    cur.execute("SELECT id FROM usuarios WHERE email = %s", (email,))
    existente = cur.fetchone()

    if existente:
        flash("E-mail já está cadastrado, faça login ou use outro.", "danger")
        cur.close()
        conn.close()
        return redirect(url_for("auth.login"))

    try:
        hash_senha = generate_password_hash(senha)
        cur.execute(
            "INSERT INTO usuarios (nome, email, senha, role) VALUES (%s, %s, %s, %s)",
            (nome, email, hash_senha, "cliente")
        )
        conn.commit()
        flash("Conta criada com sucesso! Faça login.", "success")
    except mysql.connector.Error as err:
        flash(f"Erro ao criar conta: {err}", "danger")
    finally:
        cur.close()
        conn.close()

    return redirect(url_for("auth.login"))

# ------------------------
# LOGOUT
# ------------------------
@auth_bp.route('/logout')
def logout():
    session.pop("user", None)
    flash("Você saiu da sua conta.", "info")
    return redirect(url_for("auth.login"))
