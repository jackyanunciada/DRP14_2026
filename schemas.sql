CREATE TABLE IF NOT EXISTS pedidos (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  cliente TEXT NOT NULL,
  descricao TEXT NOT NULL,
  quantidade_variedade TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'Pendente',
  tipo_entrega TEXT NOT NULL DEFAULT 'Retirada',
  taxa_entrega REAL NOT NULL DEFAULT 0,
  valor_total REAL NOT NULL DEFAULT 0,
  prioridade TEXT NOT NULL DEFAULT 'Média',
  criado_em TEXT NOT NULL DEFAULT (datetime('now','localtime'))
);