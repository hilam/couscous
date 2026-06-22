# PostgreSQL local como store — single-device

Usamos PostgreSQL 16 via Docker Compose como banco de dados, mesmo sendo um
aplicativo single-device offline-first. A alternativa óbvia seria SQLite, que
eliminaria a dependência de Docker e simplificaria o setup.

Mas o PostgreSQL nos dá tsvector para busca full-text (Sprint 5 do plano),
um ecossistema de indexes mais rico, e a possibilidade de evoluir para
multi-dispositivo no futuro sem trocar de banco. Para um leitor de notícias
com ~1000+ artigos/mês, o custo do Docker é aceitável frente ao custo de
migração de banco depois.

A contrapartida é que o setup inicial é mais pesado (Docker + banco separado)
e o offline requer que o Docker esteja rodando localmente — o que é aceitável
para um desktop app.
