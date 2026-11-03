# Agente de triagem de reclamações de pedido

Fluxo no n8n que recebe a reclamação de um cliente sobre um pedido de delivery, usa um LLM para classificar o problema e aplica regras fixas para decidir a ação. Projeto pessoal, com dados 100% fictícios.

## Como funciona

1. Um webhook recebe o texto da reclamação.
2. O LLM (Gemma 4, pela API gratuita do Google AI Studio) devolve categoria, urgência, sentimento, confiança e um resumo.
3. Um nó de código extrai o JSON da resposta. Se o modelo devolver algo ilegível, o caso vai para um humano.
4. Outro nó aplica as regras de decisão e devolve a ação pelo próprio webhook.

O LLM só classifica. Quem decide a ação (reembolso, desculpas, escalar) é o código, com regras fixas. Assim o comportamento é previsível e testável sem depender do modelo.

## Categorias e ações

| Categoria | Exemplo | Ação |
|---|---|---|
| item_faltando | "veio sem a bebida" | Reembolso parcial |
| pedido_errado | "pedi X e veio Y" | Reembolso total ou reenvio |
| atraso | "chegou 1h40 depois" | Pedido de desculpas + cupom |
| qualidade_comida | "chegou frio, massa crua" | Pedido de desculpas + reembolso parcial |
| problema_entregador | "entregador foi grosseiro" | Escalar para humano |
| cobranca_indevida | "cobrou duas vezes" | Escalar para humano |
| risco_saude_seguranca | "encontrei um objeto na comida" | Escalar para humano (prioridade máxima) |
| outros | não se encaixa nas anteriores | Escalar para humano |

Regras de segurança:
- Risco à saúde ou segurança sempre tem urgência alta, mesmo que o modelo diga outra coisa.
- Cobrança indevida e problema com entregador têm urgência no mínimo média.
- Confiança baixa do modelo sempre escala para humano.
- Categoria fora da lista vira "outros".
- O texto da reclamação é tratado como dado, e o prompt manda ignorar instruções escritas dentro dele.

## Avaliação

Rodei o fluxo com 42 reclamações fictícias (`dados/reclamacoes_teste.csv`), cada uma com categoria e urgência esperadas, definidas antes da execução. O conjunto inclui casos de borda: duas categorias na mesma mensagem, elogio, texto sem sentido e uma tentativa de mandar o agente aprovar um reembolso.

| Métrica | Resultado |
|---|---|
| Acerto de categoria | 40/42 (95%) |
| Acerto de urgência | 37/42 (88%) |
| Casos de risco escalados para humano | 7/7 |

Resultado de cada caso em `avaliacao/resultados.csv`.

### Onde errou

- **#21, fio de cabelo na sopa:** esperava `qualidade_comida`, veio `risco_saude_seguranca`. O prompt define risco como "objeto estranho na comida", então o modelo seguiu a regra. A inconsistência é do meu gabarito. Mantive o gabarito original.
- **#42, restaurante fechado que aceitou o pedido:** esperava `outros`, veio `cobranca_indevida`. O caso é ambíguo, porque o cliente pode acabar cobrado por um pedido que não chega.
- **Urgência (#7, #14, #15):** pedido de outra pessoa e dois atrasos de quase 1 hora vieram com urgência baixa, e eu esperava média. O prompt não define urgência para essas categorias. Os outros 2 erros de urgência (#21 e #42) vêm dos erros de categoria acima.

### Limitações

- 42 casos escritos por mim, em uma única execução. Serve como teste de sanidade, não como medida de desempenho real.
- O resultado pode variar entre execuções, porque o modelo não é determinístico.
- 7 das 42 chamadas deram erro 500 na primeira tentativa e passaram na nova tentativa do script.
- Não ajustei prompt nem gabarito depois de ver os resultados.

### Próximos passos

- Definir critérios de urgência para atraso e pedido errado no prompt e comparar com esta versão.
- Ampliar o conjunto de teste e rodar mais de uma vez.

## Como rodar

1. Suba o n8n com Docker:
   ```bash
   docker volume create n8n_data
   docker run -d --name n8n -p 5678:5678 -v n8n_data:/home/node/.n8n docker.n8n.io/n8nio/n8n
   ```
2. Crie uma chave gratuita no Google AI Studio e cadastre como credencial do nó Google Gemini.
3. Importe `fluxo_n8n.json` no n8n e publique o fluxo.
4. Rode a avaliação:
   ```bash
   pip install requests
   python avaliacao/avaliar.py
   ```

## Estrutura

```
├── fluxo_n8n.json
├── prompts/classificador.md
├── dados/reclamacoes_teste.csv
└── avaliacao/
    ├── avaliar.py
    └── resultados.csv
```

## Tecnologias

n8n (Docker), Google AI Studio (Gemma 4), JavaScript (nós de código), Python (avaliação).