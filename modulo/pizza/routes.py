from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import mysql.connector

pizza_bp = Blueprint("pizza", __name__, template_folder="templates")

# ------------------------
# CONEXÃO
# ------------------------
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        database="delivery",
        user="root",       # ajuste conforme seu ambiente
        password=""        # ajuste se tiver senha
    )

# ------------------------
# LISTAR SABORES + BORDAS + BEBIDAS
# ------------------------
@pizza_bp.route("/monte-pizza", methods=["GET", "POST"])
def monte_pizza():
    if request.method == "POST":
        if not session.get("user"):
            flash("Você precisa estar logado para montar uma pizza!", "warning")
            return redirect(url_for("auth.login"))

        usuario_id = session["user"]["id"]
        tamanho = request.form.get("size")
        quant_sabores = request.form.get("quantSabores")
        sabores_ids = request.form.getlist("sabores")
        borda_id = request.form.get("borda_id")
        bebidas_ids = request.form.getlist("bebidas")
        observacao = request.form.get("observacao", "")

        if not tamanho or not sabores_ids:
            flash("Selecione tamanho e pelo menos um sabor!", "danger")
            return redirect(url_for("pizza.monte_pizza"))

        conn = get_db_connection()
        cur = conn.cursor()

        try:
            # calcula preço base pela média dos sabores escolhidos
            format_ids = ",".join(["%s"] * len(sabores_ids))
            cur.execute(f"""
                SELECT preco 
                FROM precos_pizza 
                WHERE sabor_id IN ({format_ids}) AND tamanho=%s
            """, (*sabores_ids, tamanho))
            precos_sabores = [row[0] for row in cur.fetchall()]

            if not precos_sabores:
                flash("Erro ao calcular preços dos sabores.", "danger")
                return redirect(url_for("pizza.monte_pizza"))

            preco_base = sum(precos_sabores) / len(precos_sabores)

            # desconto/acréscimo por quantidade
            if len(sabores_ids) == 1:
                preco_base *= 1.20
            elif len(sabores_ids) == 3:
                preco_base *= 0.90
            elif len(sabores_ids) == 4:
                preco_base *= 0.80

            preco_total = preco_base

            # borda
            if borda_id and borda_id.isdigit():
                cur.execute("SELECT preco FROM bordas WHERE id=%s", (borda_id,))
                row = cur.fetchone()
                if row:
                    preco_total += row[0]

            # bebidas
            bebidas_escolhidas = []
            if bebidas_ids:
                format_bebidas = ",".join(["%s"] * len(bebidas_ids))
                cur.execute(f"SELECT id, preco FROM produtos WHERE id IN ({format_bebidas})", tuple(bebidas_ids))
                for bid, preco in cur.fetchall():
                    preco_total += preco
                    bebidas_escolhidas.append(bid)

            # cria pizza
            cur.execute("""
                INSERT INTO pizzas (usuario_id, tamanho, borda_id, observacao, preco_total)
                VALUES (%s, %s, %s, %s, %s)
            """, (usuario_id, tamanho, borda_id if borda_id else None, observacao, preco_total))
            pizza_id = cur.lastrowid

            # sabores da pizza
            for sid in sabores_ids:
                cur.execute("INSERT INTO pizza_sabores (pizza_id, sabor_id) VALUES (%s, %s)", (pizza_id, sid))

            # insere bebidas como itens normais
            for bid in bebidas_escolhidas:
                cur.execute("""
                    INSERT INTO itens_pedido (pedido_id, produto_id, quantidade, preco_unitario)
                    VALUES (%s, %s, %s, (SELECT preco FROM produtos WHERE id=%s))
                """, (pizza_id, bid, 1, bid))

            conn.commit()
            flash("🍕 Pizza adicionada com sucesso!", "success")
        except mysql.connector.Error as err:
            conn.rollback()
            flash(f"Erro ao salvar pizza: {err}", "danger")
        finally:
            cur.close()
            conn.close()

        return redirect(url_for("pizza.monte_pizza"))

    # GET → listar opções
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)

    # sabores + preços por tamanho
    cur.execute("""
        SELECT s.id, s.nome AS sabor, c.nome AS categoria, s.categoria_id,
               MAX(CASE WHEN p.tamanho='P' THEN p.preco END) AS preco_p,
               MAX(CASE WHEN p.tamanho='M' THEN p.preco END) AS preco_m,
               MAX(CASE WHEN p.tamanho='G' THEN p.preco END) AS preco_g
        FROM sabores_pizza s
        JOIN categorias_sabor c ON c.id = s.categoria_id
        JOIN precos_pizza p ON p.sabor_id = s.id
        GROUP BY s.id, s.nome, c.nome, s.categoria_id
        ORDER BY c.nome, s.nome
    """)
    sabores = cur.fetchall()

    # categorias de sabor (para modais admin)
    cur.execute("SELECT id, nome FROM categorias_sabor ORDER BY nome")
    categorias = cur.fetchall()

    # bordas
    cur.execute("SELECT id, nome, preco FROM bordas ORDER BY nome")
    bordas = cur.fetchall()

    # bebidas
    cur.execute("""
        SELECT p.id, p.nome, p.preco
        FROM produtos p
        JOIN categorias c ON c.id = p.categoria_id
        WHERE c.nome = 'Bebidas' AND p.ativo = TRUE
        ORDER BY p.nome
    """)
    bebidas = cur.fetchall()

    cur.close()
    conn.close()

    return render_template(
        "monte_pizza.html",
        sabores=sabores,
        categorias=categorias,
        bordas=bordas,
        bebidas=bebidas,
        user=session.get("user"),
        active_page="pizza"
    )
