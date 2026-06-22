# Tags em entries, não em feeds

Tags são atribuídas a entries individuais, não a feeds. O modelo `FeedTag`
existente no código é dead code e será substituído por `EntryTag`.

A alternativa — tags em feeds (uma tag no feed se aplica a todos os artigos
dele) — é mais simples de implementar e requer menos UI. Mas o usuário quer
marcar artigos específicos com rótulos como "urgente" ou "opinião", que não
fazem sentido no nível do feed. Tags em entries oferecem granularidade real
para organização e futura busca.

A extração automática de tags via SLM (Small Language Model) está no radar
como pós-MVP, mas o modelo `EntryTag` já suporta ambos os modos (manual e
automático).
