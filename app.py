from flask import Flask, render_template
from jinja2 import ChoiceLoader, FileSystemLoader
import os  # Para gerar uma secret key segura

# Importando os blueprints
from modulo.pizza.routes import pizza_bp
from modulo.cardapio.routes import cardapio_bp
from modulo.auth.routes import auth_bp
from modulo.base.routes import base_bp  
from modulo.administracao.routes import administracao_bp 

def create_app():
    app = Flask(__name__)
    app.secret_key = os.environ.get('SECRET_KEY') or 'uma_chave_super_secreta_e_unica_!@#123'

    # Carregar templates de múltiplas pastas
    app.jinja_loader = ChoiceLoader([
        FileSystemLoader('modulo/base'),
        FileSystemLoader('modulo/pizza'),
        FileSystemLoader('modulo/cardapio'),
        FileSystemLoader('modulo/auth'),
        FileSystemLoader('modulo/administracao'), 
    ])

    # Registrar blueprints
    app.register_blueprint(base_bp)
    app.register_blueprint(pizza_bp)
    app.register_blueprint(cardapio_bp, url_prefix='/cardapio')
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(administracao_bp, url_prefix='/admin') 

    @app.route('/')
    def home():
        return render_template('base.html')

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
