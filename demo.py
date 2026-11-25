"""Demonstração do modelo com dados fictícios."""
from modelos import (
    Cliente, Consultoria, Equipe, Instalacao, Manutencao, OrdemServico,
    RelatorioServicos,
)


def main() -> None:
    cliente = Cliente("Padaria Scapim")
    equipe = Equipe("Equipe Técnica")
    ordens = [
        OrdemServico(1, cliente, equipe, Instalacao()),
        OrdemServico(2, cliente, equipe, Manutencao()),
        OrdemServico(3, cliente, equipe, Consultoria()),
    ]

    for ordem in ordens:
        print(f"OS {ordem.numero} | {type(ordem.servico).__name__} | "
              f"{ordem.cliente.nome} | {ordem.equipe.nome}")
        for numero, item in enumerate(ordem.itens, start=1):
            print(f"  {numero}. {item.descricao}")

    instalacao = ordens[0]
    instalacao.marcar_etapa(1)
    try:
        instalacao.concluir()
    except ValueError as erro:
        print(f"OS 1 ainda aberta. {erro}")

    instalacao.marcar_etapa(2)
    instalacao.concluir()
    print("OS 1 concluída.")

    resumo = RelatorioServicos().resumir(ordens)
    print(f"Relatório | Abertas: {resumo['abertas']} | "
          f"Concluídas: {resumo['concluidas']}")


if __name__ == "__main__":
    main()
