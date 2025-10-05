from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import mysql.connector

cardapio_bp = Blueprint('cardapio', __name__, template_folder='.')

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        database="delivery",
        user="root",   # padrão do XAMPP
        password=""    # normalmente vazio no XAMPP
    )

# ------------------------
# LISTAR CATEGORIAS
# ------------------------
@cardapio_bp.route('/')
def menu():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, nome, descricao, imagem_url FROM categorias ORDER BY id")
    categorias = cur.fetchall()
    cur.close()
    conn.close()

    user = session.get("user")
    return render_template(
        'cardapio.html',
        categorias=categorias,
        user=user,
        active_page='menu'
    )

# ------------------------
# ADICIONAR CATEGORIA
# ------------------------
@cardapio_bp.route('/add', methods=['POST'])
def add_categoria():
    if not session.get("user") or session["user"]["role"] != "admin":
        flash("Acesso negado!", "danger")
        return redirect(url_for("cardapio.menu"))

    nome = request.form.get("nome").strip()
    descricao = request.form.get("descricao").strip()
    imagem = request.form.get("imagem_url").strip() if request.form.get("imagem_url") else None

    if not nome or not descricao:
        flash("Nome e descrição são obrigatórios.", "warning")
        return redirect(url_for("cardapio.menu"))

    conn = get_db_connection()
    cur = conn.cursor()

    # verificar duplicados
    cur.execute("SELECT id FROM categorias WHERE nome = %s", (nome,))
    existe = cur.fetchone()
    if existe:
        flash("Já existe uma categoria com esse nome.", "danger")
        cur.close()
        conn.close()
        return redirect(url_for("cardapio.menu"))

    try:
        cur.execute(
            "INSERT INTO categorias (nome, descricao, imagem_url) VALUES (%s, %s, %s)",
            (nome, descricao, imagem)
        )
        conn.commit()
        flash("Categoria adicionada com sucesso!", "success")
    except mysql.connector.Error as err:
        flash(f"Erro ao adicionar categoria: {err}", "danger")
    finally:
        cur.close()
        conn.close()

    return redirect(url_for("cardapio.menu"))

# ------------------------
# EDITAR CATEGORIA
# ------------------------
@cardapio_bp.route('/edit/<int:cat_id>', methods=['POST'])
def edit_categoria(cat_id):
    if not session.get("user") or session["user"]["role"] != "admin":
        flash("Acesso negado!", "danger")
        return redirect(url_for("cardapio.menu"))

    nome = request.form.get("nome").strip()
    descricao = request.form.get("descricao").strip()
    imagem = request.form.get("imagem_url").strip() if request.form.get("imagem_url") else None

    if not nome or not descricao:
        flash("Nome e descrição são obrigatórios.", "warning")
        return redirect(url_for("cardapio.menu"))

    conn = get_db_connection()
    cur = conn.cursor()

    # garantir que não edite para um nome já existente em outra categoria
    cur.execute("SELECT id FROM categorias WHERE nome = %s AND id != %s", (nome, cat_id))
    existe = cur.fetchone()
    if existe:
        flash("Já existe outra categoria com esse nome.", "danger")
        cur.close()
        conn.close()
        return redirect(url_for("cardapio.menu"))

    try:
        cur.execute(
            "UPDATE categorias SET nome=%s, descricao=%s, imagem_url=%s WHERE id=%s",
            (nome, descricao, imagem, cat_id)
        )
        conn.commit()
        flash("Categoria atualizada com sucesso!", "success")
    except mysql.connector.Error as err:
        flash(f"Erro ao atualizar categoria: {err}", "danger")
    finally:
        cur.close()
        conn.close()

    return redirect(url_for("cardapio.menu"))

# ------------------------
# REMOVER CATEGORIA
# ------------------------
@cardapio_bp.route('/delete/<int:cat_id>')
def delete_categoria(cat_id):
    if not session.get("user") or session["user"]["role"] != "admin":
        flash("Acesso negado!", "danger")
        return redirect(url_for("cardapio.menu"))

    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM categorias WHERE id = %s", (cat_id,))
        conn.commit()
        flash("Categoria removida com sucesso!", "info")
    except mysql.connector.Error as err:
        flash(f"Erro ao remover categoria: {err}", "danger")
    finally:
        cur.close()
        conn.close()

    return redirect(url_for("cardapio.menu"))
