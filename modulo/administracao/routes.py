from flask import Blueprint, session, flash, redirect, url_for, render_template, request
import mysql.connector
from werkzeug.security import generate_password_hash

administracao_bp = Blueprint("administracao", __name__, template_folder=".")

# ------------------------
# Conexão
# ------------------------
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        database="delivery",
        user="root",
        password=""
    )

# ------------------------
# Painel de Administração
# ------------------------
@administracao_bp.route("/config-site/update", methods=["GET", "POST"])
def update_config_site():
    # Acesso apenas admin
    if not session.get("user") or session["user"]["role"] != "admin":
        flash("Acesso negado!", "danger")
        return redirect(url_for("cardapio.menu"))

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)

    # ----- Atualizar Config do Site -----
    if request.method == "POST" and request.form.get("form_type") == "site":
        nome = request.form.get("nome_restaurante") or "Seu Restaurante"
        logo = request.form.get("logo_url") or "/static/logo.png"
        banner = request.form.get("banner_url") or "/static/banner.jpg"
        instagram = request.form.get("instagram") or ""
        facebook = request.form.get("facebook") or ""
        whatsapp = request.form.get("whatsapp") or ""

        cur.execute("""
            INSERT INTO configuracoes_site 
            (nome_restaurante, logo_url, banner_url, instagram, facebook, whatsapp)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (nome, logo, banner, instagram, facebook, whatsapp))
        conn.commit()
        flash("Configurações do site atualizadas!", "success")

    # ----- Criar Usuário -----
    if request.method == "POST" and request.form.get("form_type") == "user":
        nome = request.form.get("nome")
        email = request.form.get("email")
        senha = request.form.get("senha")
        role = request.form.get("role")

        if not nome or not email or not senha:
            flash("Preencha todos os campos!", "warning")
        else:
            try:
                cur.execute("SELECT id FROM usuarios WHERE email=%s", (email,))
                if cur.fetchone():
                    flash("E-mail já cadastrado.", "danger")
                else:
                    hash_senha = generate_password_hash(senha)
                    cur.execute(
                        "INSERT INTO usuarios (nome, email, senha, role) VALUES (%s,%s,%s,%s)",
                        (nome, email, hash_senha, role)
                    )
                    conn.commit()
                    flash("Usuário criado com sucesso!", "success")
            except Exception as e:
                flash(f"Erro: {e}", "danger")

    # ----- Carregar dados -----
    cur.execute("SELECT * FROM configuracoes_site ORDER BY id DESC LIMIT 1")
    config = cur.fetchone()

    cur.execute("SELECT id, nome, email, role FROM usuarios ORDER BY id DESC")
    usuarios = cur.fetchall()

    cur.close()
    conn.close()

    return render_template("config_site.html", site_config=config, usuarios=usuarios, user=session.get("user"))


# ------------------------
# Editar Usuário
# ------------------------
@administracao_bp.route("/usuarios/edit/<int:user_id>", methods=["POST"])
def edit_user(user_id):
    if not session.get("user") or session["user"]["role"] != "admin":
        flash("Acesso negado!", "danger")
        return redirect(url_for("administracao.update_config_site"))

    nome = request.form.get("nome")
    email = request.form.get("email")
    role = request.form.get("role")

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute(
            "UPDATE usuarios SET nome=%s, email=%s, role=%s WHERE id=%s",
            (nome, email, role, user_id)
        )
        conn.commit()
        flash("Usuário atualizado com sucesso!", "success")
    except Exception as e:
        flash(f"Erro: {e}", "danger")
    finally:
        cur.close()
        conn.close()

    return redirect(url_for("administracao.update_config_site"))


# ------------------------
# Excluir Usuário
# ------------------------
@administracao_bp.route("/usuarios/delete/<int:user_id>")
def delete_user(user_id):
    if not session.get("user") or session["user"]["role"] != "admin":
        flash("Acesso negado!", "danger")
        return redirect(url_for("administracao.update_config_site"))

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute("DELETE FROM usuarios WHERE id=%s", (user_id,))
        conn.commit()
        flash("Usuário removido com sucesso!", "info")
    except Exception as e:
        flash(f"Erro: {e}", "danger")
    finally:
        cur.close()
        conn.close()

    return redirect(url_for("administracao.update_config_site"))
