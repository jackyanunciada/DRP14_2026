CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    senha TEXT NOT NULL,
    cpf TEXT,
    data_nascimento TEXT,
    endereco TEXT,
    perfil TEXT NOT NULL DEFAULT 'cliente'
);

CREATE TABLE IF NOT EXISTS pedidos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER,
    cliente TEXT NOT NULL,
    descricao TEXT NOT NULL,
    quantidade_variedade TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'Pendente',
    tipo_entrega TEXT NOT NULL DEFAULT 'Retirada',
    taxa_entrega REAL NOT NULL DEFAULT 0,
    valor_total REAL NOT NULL DEFAULT 0,
    prioridade TEXT NOT NULL DEFAULT 'Média',
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
);

CREATE TABLE IF NOT EXISTS notificacoes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER,
    mensagem TEXT NOT NULL,
    lida INTEGER DEFAULT 0,
    criada_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
);