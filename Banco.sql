-- ========================
-- CRIAÇÃO DO BANCO
-- ========================
DROP DATABASE IF EXISTS delivery;
CREATE DATABASE delivery;
USE delivery;

-- ========================
-- USUÁRIOS E ENDEREÇOS
-- ========================
CREATE TABLE usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    telefone VARCHAR(20),
    senha VARCHAR(255) NOT NULL,
    role ENUM('cliente','admin','entregador') DEFAULT 'cliente',
    data_aniversario DATE,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE enderecos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT NOT NULL,
    logradouro VARCHAR(150) NOT NULL,
    numero VARCHAR(20),
    bairro VARCHAR(100),
    cidade VARCHAR(100),
    estado CHAR(2),
    cep VARCHAR(15),
    complemento VARCHAR(150),
    padrao BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
);

-- ========================
-- CATEGORIAS E PRODUTOS
-- ========================
CREATE TABLE categorias (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    descricao TEXT,
    imagem_url VARCHAR(255),
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE produtos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(150) NOT NULL,
    descricao TEXT,
    preco DECIMAL(10,2) NOT NULL,
    imagem_url VARCHAR(255),
    categoria_id INT,
    ativo BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (categoria_id) REFERENCES categorias(id) ON DELETE SET NULL
);

-- ========================
-- PIZZAS
-- ========================

-- Tipos de sabor (Especiais, Doces, Premium, etc.)
CREATE TABLE categorias_sabor (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL UNIQUE
);

-- Sabores (Calabresa, Beijinho, etc.)
CREATE TABLE sabores_pizza (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    categoria_id INT NOT NULL,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (categoria_id) REFERENCES categorias_sabor(id) ON DELETE CASCADE
);

-- Preços por tamanho
CREATE TABLE precos_pizza (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sabor_id INT NOT NULL,
    tamanho ENUM('P','M','G') NOT NULL,
    preco DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (sabor_id) REFERENCES sabores_pizza(id) ON DELETE CASCADE
);

-- Bordas
CREATE TABLE bordas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    preco DECIMAL(10,2) NOT NULL DEFAULT 0
);

-- Pizza montada pelo cliente
CREATE TABLE pizzas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT,
    tamanho ENUM('P','M','G') NOT NULL,
    borda_id INT,
    observacao TEXT,
    preco_total DECIMAL(10,2) NOT NULL,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE SET NULL,
    FOREIGN KEY (borda_id) REFERENCES bordas(id) ON DELETE SET NULL
);

-- Sabores escolhidos em uma pizza (1 até 4 sabores)
CREATE TABLE pizza_sabores (
    id INT AUTO_INCREMENT PRIMARY KEY,
    pizza_id INT NOT NULL,
    sabor_id INT NOT NULL,
    FOREIGN KEY (pizza_id) REFERENCES pizzas(id) ON DELETE CASCADE,
    FOREIGN KEY (sabor_id) REFERENCES sabores_pizza(id) ON DELETE CASCADE
);

-- ========================
-- CONFIGURAÇÕES DO SITE
-- ========================
CREATE TABLE configuracoes_site (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome_restaurante VARCHAR(150) NOT NULL DEFAULT 'Seu Restaurante',
    logo_url VARCHAR(255) DEFAULT '/static/logo.png',
    banner_url VARCHAR(255) DEFAULT '/static/banner.jpg',
    instagram VARCHAR(255) DEFAULT '#',
    facebook VARCHAR(255) DEFAULT '#',
    whatsapp VARCHAR(50) DEFAULT '',
    atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- ========================
-- DADOS INICIAIS
-- ========================

-- Usuário administrador
INSERT INTO usuarios (nome,email,senha,role)
VALUES (
    'Administrador',
    'admin@restaurante.com',
    'scrypt:32768:8:1$UhIodJR6AgGYGnNQ$7817f1b45695cafd02104dc34fb9b7a06d4a0373e86f8852e5e513a6d4ee8796fcc802757eed1793e6abed0e3c2e24f1b5c1fe690a042bf81bf2c975b312eb30',
    'admin'
);

-- Categorias gerais
INSERT INTO categorias (nome,descricao,imagem_url) VALUES
('Pizzas','Deliciosas pizzas artesanais','/static/uploads/categorias/pizzas.jpg'),
('Lanches','Hambúrgueres e sanduíches','/static/uploads/categorias/lanches.jpg'),
('Bebidas','Sucos e refrigerantes','/static/uploads/categorias/bebidas.jpg'),
('Combos','Ofertas especiais','/static/uploads/categorias/combos.jpg');

-- Bordas
INSERT INTO bordas (nome,preco) VALUES
('Sem borda',0),
('Catupiry',8),
('Cheddar',8),
('Chocolate',10);

-- Categorias de sabor
INSERT INTO categorias_sabor (nome) VALUES
('Especiais'),
('Doces'),
('Premium');

-- Exemplo de sabores
INSERT INTO sabores_pizza (nome, categoria_id) VALUES
('Calabresa', 1),
('Frango com Catupiry', 1),
('Beijinho', 2),
('Brigadeiro', 2),
('Camarão Premium', 3);

-- Preços exemplo
INSERT INTO precos_pizza (sabor_id, tamanho, preco) VALUES
(1,'P',25.00),(1,'M',32.00),(1,'G',39.00),
(2,'P',28.00),(2,'M',36.00),(2,'G',44.00),
(3,'P',30.00),(3,'M',38.00),(3,'G',46.00),
(4,'P',31.00),(4,'M',39.00),(4,'G',47.00),
(5,'P',50.00),(5,'M',65.00),(5,'G',80.00);
