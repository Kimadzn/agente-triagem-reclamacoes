# Agente de triagem de reclamações de pedido

Projeto pessoal em construção: um fluxo no n8n que recebe a reclamação de um cliente sobre um pedido de delivery, usa um LLM via API para classificar o problema e aplica regras para decidir a ação. Todos os dados são fictícios.

## Categorias e ações

| Categoria | Exemplo | Ação |
|---|---|---|
| item_faltando | "veio sem a bebida" | reembolso parcial |
| pedido_errado | "pedi X e veio Y" | reembolso total ou reenvio |
| atraso | "chegou 1h40 depois" | pedido de desculpas + cupom |
| qualidade_comida | "chegou frio, massa crua" | pedido de desculpas + reembolso parcial |
| problema_entregador | "entregador foi grosseiro" | escalar para humano |
| cobranca_indevida | "cobrou duas vezes" | escalar para humano |
| risco_saude_seguranca | "encontrei um objeto na comida" | escalar para humano com prioridade máxima |
| outros | não se encaixa nas anteriores | escalar para humano |

Urgência: baixa, média ou alta. Risco à saúde ou segurança é sempre alta.
Sentimento: negativo, neutro ou muito_negativo.
Na dúvida, o agente escala para um humano.

## Status

- [x] Categorias e regras
- [ ] Prompt do classificador
- [ ] Fluxo no n8n
- [ ] Reclamações de teste
- [ ] Script de avaliação
- [ ] README final