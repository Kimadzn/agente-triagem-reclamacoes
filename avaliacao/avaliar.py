import csv
import time

import requests

URL = "http://localhost:5678/webhook/reclamacao"
ARQUIVO_TESTE = "dados/reclamacoes_teste.csv"
ARQUIVO_SAIDA = "avaliacao/resultados.csv"
PAUSA_SEGUNDOS = 4   # pausa entre chamadas, para não estourar o limite gratuito
TENTATIVAS = 3


def classificar(texto):
    """Manda a reclamação para o fluxo do n8n e devolve o JSON da resposta."""
    for tentativa in range(1, TENTATIVAS + 1):
        try:
            resposta = requests.post(URL, json={"reclamacao": texto}, timeout=120)
            resposta.raise_for_status()
            dados = resposta.json()
            return dados[0] if isinstance(dados, list) else dados
        except (requests.RequestException, ValueError) as erro:
            print(f"   tentativa {tentativa} falhou: {erro}")
            time.sleep(10)
    return None


def main():
    with open(ARQUIVO_TESTE, encoding="utf-8-sig", newline="") as f:
        casos = list(csv.DictReader(f))

    resultados = []
    for i, caso in enumerate(casos, start=1):
        print(f"[{i}/{len(casos)}] {caso['reclamacao'][:60]}")
        saida = classificar(caso["reclamacao"]) or {}

        resultados.append({
            "id": caso["id"],
            "reclamacao": caso["reclamacao"],
            "categoria_esperada": caso["categoria_esperada"],
            "categoria_obtida": saida.get("categoria", "FALHA"),
            "urgencia_esperada": caso["urgencia_esperada"],
            "urgencia_obtida": saida.get("urgencia", "FALHA"),
            "confianca": saida.get("confianca", ""),
            "acao": saida.get("acao", ""),
            "escalar_humano": saida.get("escalar_humano", ""),
        })
        time.sleep(PAUSA_SEGUNDOS)

    with open(ARQUIVO_SAIDA, "w", encoding="utf-8", newline="") as f:
        escritor = csv.DictWriter(f, fieldnames=resultados[0].keys())
        escritor.writeheader()
        escritor.writerows(resultados)

    total = len(resultados)
    acertos_cat = sum(r["categoria_esperada"] == r["categoria_obtida"] for r in resultados)
    acertos_urg = sum(r["urgencia_esperada"] == r["urgencia_obtida"] for r in resultados)
    falhas = sum(r["categoria_obtida"] == "FALHA" for r in resultados)

    riscos = [r for r in resultados if r["categoria_esperada"] == "risco_saude_seguranca"]
    riscos_escalados = sum(r["escalar_humano"] is True for r in riscos)

    print("\n===== RESULTADO =====")
    print(f"Reclamações testadas: {total} (falhas de chamada: {falhas})")
    print(f"Acerto de categoria: {acertos_cat}/{total} ({acertos_cat / total:.0%})")
    print(f"Acerto de urgência:  {acertos_urg}/{total} ({acertos_urg / total:.0%})")
    print(f"Casos de risco escalados para humano: {riscos_escalados}/{len(riscos)}")

    print("\nErros de categoria:")
    for r in resultados:
        if r["categoria_esperada"] != r["categoria_obtida"]:
            print(f" - #{r['id']}: esperado {r['categoria_esperada']}, obtido {r['categoria_obtida']}")


if __name__ == "__main__":
    main()