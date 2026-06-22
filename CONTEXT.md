# CousCous

Um leitor de RSS/Atom desktop para um único usuário por instância, focado em leitura
rápida e organizada de notícias com suporte offline.

## Language

**Feed**:
Uma fonte RSS ou Atom assinada pelo usuário. Contém metadados (título, link, etag) e
é o organizador primário do conteúdo.
_Avoid_: Fonte, canal, source

**Entry**:
Um artigo individual dentro de um feed. É a unidade de consumo — o que o usuário lê.
Pode estar lida ou não lida, e pode ser marcada como importante.
_Avoid_: Notícia, post, item

**Category**:
Pasta hierárquica que organiza **feeds**. Um feed pertence a exatamente zero ou uma
categoria. Categorias podem ter subcategorias (auto-relacionamento via parent_id).
_Avoid_: Pasta, grupo, label

**Tag**:
Rótulo textual atribuído manualmente a uma **entry**. Uma entry pode ter múltiplas tags.
Tags são livremente escolhidas pelo usuário (não pré-definidas).
_Avoid_: Etiqueta, marcador, categoria

**User**:
Pessoa que possui feeds, entries, categorias e tags. O sistema é single-device e o user
é autenticado localmente (senha bcrypt ou OAuth).

**Read**:
Estado booleano de uma entry: lida (`read = 1`) ou não lida (`read = 0`).
_Avoid_: Visualizado, visto

**Important**:
Estado booleano de uma entry: importante/estrelada (`important = 1`) ou normal
(`important = 0`). Entries importantes são preservadas durante a limpeza automática.
_Avoid_: Favorito, estrelado, destacado

**Refresh**:
Operação de buscar entries novas de um feed via HTTP. Pode ser single feed ou
todos os feeds do usuário (em paralelo, com limite de concorrência).

**Purge**:
Limpeza automática de entries antigas e lidas, configurável por período
(dias/semanas/meses). Entries importantes não são afetadas.
