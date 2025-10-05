from flask import Blueprint, g, session, flash, redirect, url_for, render_template, request
import mysql.connector
from datetime import datetime

base_bp = Blueprint("base", __name__, template_folder=".")

# ------------------------
# Conexão com Banco
# ------------------------
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        database="delivery",
        user="root",
        password=""
    )

# ------------------------
# Middleware - Carregar Config do Site
# ------------------------
@base_bp.before_app_request
def carregar_configuracoes():
    """Carrega a última configuração do site em cada request"""
    try:
        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM configuracoes_site ORDER BY id DESC LIMIT 1")
        g.site_config = cur.fetchone() or {
            "nome_restaurante": "Seu Restaurante",
            "logo_url": "/static/logo.png",
            "banner_url": "/static/banner.jpg",
            "instagram": "#",
            "facebook": "#",
            "whatsapp": ""
        }
        cur.close()
        conn.close()
    except mysql.connector.Error:
        # fallback se banco não responder
        g.site_config = {
            "nome_restaurante": "Seu Restaurante",
            "logo_url": "/static/logo.png",
            "banner_url": "/static/banner.jpg",
            "instagram": "#",
            "facebook": "#",
            "whatsapp": ""
        }

# ------------------------
# Context Processor
# ------------------------
@base_bp.app_context_processor
def inject_config():
    """Disponibiliza configs e infos do usuário em todos os templates"""
    return dict(
        site_config=g.get("site_config", {}),
        current_year=datetime.now().year,
        user=session.get("user")
    )

# ------------------------
# Rota para atualizar Config do Site (via modal no base.html)
# ------------------------
@base_bp.route("/config-site/update", methods=["POST"])
def update_config():
    """Atualiza configurações do site"""
    if not session.get("user") or session["user"]["role"] != "admin":
        flash("Acesso negado!", "danger")
        return redirect(url_for("cardapio.menu"))

    nome = request.form.get("nome_restaurante") or "Seu Restaurante"
    logo = request.form.get("logo_url") or "/static/logo.png"
    banner = request.form.get("banner_url") or "/static/banner.jpg"
    instagram = request.form.get("instagram") or "#"
    facebook = request.form.get("facebook") or "#"
    whatsapp = request.form.get("whatsapp") or ""

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO configuracoes_site (nome_restaurante, logo_url, banner_url, instagram, facebook, whatsapp)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (nome, logo, banner, instagram, facebook, whatsapp))
    conn.commit()
    cur.close()
    conn.close()

    flash("Configurações atualizadas com sucesso!", "success")
    return redirect(url_for("cardapio.menu"))
