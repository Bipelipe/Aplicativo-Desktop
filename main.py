"""Menu de terminal do JAM-DF para o Desk App III."""

import sqlite3
from argparse import ArgumentParser
from collections.abc import Container, Mapping
from contextlib import closing
from pathlib import Path
from sys import stdin
from time import sleep

from banco import BANCO_PADRAO, BancoDados
from modelos import Cliente, Equipe, OrdemServico, RelatorioServicos, TIPOS_SERVICO

MENU = """
--JAM-DF--
1. Cadastrar cliente
2. Listar clientes
3. Cadastrar equipe
4. Listar equipes
5. Abrir ordem de serviço
6. Listar ordens e checklists
7. Marcar etapa
8. Concluir ordem
9. Consultar relatório
10. Listar tipos de serviço
0. Sair
"""


def ler_nome(rotulo: str) -> str:
    nome = input(f"Nome {rotulo}: ").strip()
    if not nome:
        raise ValueError("Informe um nome.")
    return nome


def escolher_numero(pergunta: str, numeros: Container[int]) -> int:
    resposta = input(pergunta).strip()
    try:
        numero = int(resposta)
    except ValueError:
        raise ValueError("Digite um número válido.") from None
    if numero not in numeros:
        raise ValueError("Número não encontrado.")
    return numero


def listar_cadastros(registros: Mapping[int, Cliente | Equipe], titulo: str) -> None:
    print(titulo)
    if not registros:
        print("Nenhum registro cadastrado.")
    for numero, registro in registros.items():
        print(f"{numero}. {registro.nome}")


def listar_tipos(mostrar_etapas: bool = False) -> None:
    print("Tipos de serviço")
    for numero, (nome, classe) in TIPOS_SERVICO.items():
        print(f"{numero}. {nome}")
        if mostrar_etapas:
            for etapa in classe().gerar_checklist():
                print(f"   - {etapa}")


def abrir_ordem(banco: BancoDados) -> int:
    clientes = banco.listar_clientes()
    equipes = banco.listar_equipes()
    if not clientes or not equipes:
        raise ValueError("Cadastre um cliente e uma equipe antes de abrir uma ordem.")

    listar_cadastros(clientes, "Clientes")
    cliente_id = escolher_numero("Número do cliente: ", clientes)
    listar_cadastros(equipes, "Equipes")
    equipe_id = escolher_numero("Número da equipe: ", equipes)
    listar_tipos()
    tipo = escolher_numero("Tipo de serviço: ", TIPOS_SERVICO)
    return banco.abrir_ordem(cliente_id, equipe_id, tipo)


def listar_ordens(ordens: dict[int, OrdemServico]) -> None:
    print("Ordens de serviço")
    if not ordens:
        print("Nenhuma ordem cadastrada.")

    nomes_servicos = {classe: nome for nome, classe in TIPOS_SERVICO.values()}
    for ordem in ordens.values():
        status = "Concluída" if ordem.concluida else "Aberta"
        servico = nomes_servicos[type(ordem.servico)]
        print(f"OS {ordem.numero} | {servico} | {status}")
        print(f"  Cliente: {ordem.cliente.nome} | Equipe: {ordem.equipe.nome}")
        for numero, item in enumerate(ordem.itens, start=1):
            marca = "x" if item.concluido else " "
            print(f"  {numero}. [{marca}] {item.descricao}")


def escolher_ordem(ordens: dict[int, OrdemServico]) -> OrdemServico:
    if not ordens:
        raise ValueError("Nenhuma ordem cadastrada.")
    numero = escolher_numero("Número da ordem: ", ordens)
    return ordens[numero]


def executar_menu(banco: BancoDados) -> None:
    relatorio = RelatorioServicos()

    while True:
        print(MENU)
        try:
            opcao = input("Escolha uma opção: ").strip()
            match opcao:
                case "1":
                    cliente = Cliente(ler_nome("do cliente"))
                    numero = banco.cadastrar_cliente(cliente)
                    print(f"Cliente {numero} cadastrado.")
                case "2":
                    listar_cadastros(banco.listar_clientes(), "Clientes")
                case "3":
                    equipe = Equipe(ler_nome("da equipe"))
                    numero = banco.cadastrar_equipe(equipe)
                    print(f"Equipe {numero} cadastrada.")
                case "4":
                    listar_cadastros(banco.listar_equipes(), "Equipes")
                case "5":
                    numero = abrir_ordem(banco)
                    print(f"OS {numero} aberta.")
                case "6":
                    listar_ordens(banco.listar_ordens())
                case "7":
                    ordem = escolher_ordem(banco.listar_ordens())
                    etapas = range(1, len(ordem.itens) + 1)
                    etapa = escolher_numero("Número da etapa: ", etapas)
                    banco.marcar_etapa(ordem, etapa)
                    print(f"Etapa {etapa} da OS {ordem.numero} marcada.")
                case "8":
                    ordem = escolher_ordem(banco.listar_ordens())
                    banco.concluir_ordem(ordem)
                    print(f"OS {ordem.numero} concluída.")
                case "9":
                    resumo = relatorio.resumir(banco.listar_ordens().values())
                    print(f"Abertas: {resumo['abertas']} | Concluídas: {resumo['concluidas']}")
                case "10":
                    listar_tipos(mostrar_etapas=True)
                case "0":
                    break
                case _:
                    print("Opção inválida.")
        except ValueError as erro:
            print(erro)
        except sqlite3.Error as erro:
            print(f"Erro no banco de dados: {erro}")
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if stdin.isatty():
            sleep(1)

    print("JAM-DF encerrado.")


def main() -> None:
    argumentos = ArgumentParser(description="JAM-DF | Desk App III")
    argumentos.add_argument(
        "--banco", type=Path, default=BANCO_PADRAO,
        help="Arquivo SQLite a usar (padrão: jam_df.sqlite3 na pasta do projeto).",
    )
    caminho = argumentos.parse_args().banco

    try:
        with closing(sqlite3.connect(caminho)) as conexao:
            executar_menu(BancoDados(conexao))
    except sqlite3.Error as erro:
        argumentos.exit(1, f"Erro ao abrir o banco de dados: {erro}\n")


if __name__ == "__main__":
    main()
