CREATE TABLE IF NOT EXISTS chamados (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  titulo TEXT NOT NULL,
  descricao TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'Aberto',
  prioridade TEXT NOT NULL DEFAULT 'Média',
  criado_em TEXT NOT NULL DEFAULT (datetime('now','localtime'))
);
