"""Persistência dos clientes, equipes, ordens e checklists no SQLite."""

from itertools import groupby
from pathlib import Path
from sqlite3 import Connection

from modelos import Cliente, Equipe, ItemChecklist, OrdemServico, TIPOS_SERVICO


BANCO_PADRAO = Path(__file__).resolve().with_name("jam_df.sqlite3")


class BancoDados:
    def __init__(self, conexao: Connection):
        self.conexao = conexao
        self.conexao.execute("PRAGMA foreign_keys = ON")
        self.conexao.executescript("""
            CREATE TABLE IF NOT EXISTS clientes (
                id INTEGER PRIMARY KEY,
                nome TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS equipes (
                id INTEGER PRIMARY KEY,
                nome TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS ordens (
                numero INTEGER PRIMARY KEY,
                cliente_id INTEGER NOT NULL REFERENCES clientes(id),
                equipe_id INTEGER NOT NULL REFERENCES equipes(id),
                tipo INTEGER NOT NULL,
                concluida INTEGER NOT NULL DEFAULT 0 CHECK (concluida IN (0, 1))
            );

            CREATE TABLE IF NOT EXISTS itens_checklist (
                ordem_numero INTEGER NOT NULL REFERENCES ordens(numero),
                numero INTEGER NOT NULL,
                descricao TEXT NOT NULL,
                concluido INTEGER NOT NULL DEFAULT 0 CHECK (concluido IN (0, 1)),
                PRIMARY KEY (ordem_numero, numero)
            );
        """)

    def cadastrar_cliente(self, cliente: Cliente) -> int:
        with self.conexao:
            registro = self.conexao.execute(
                "INSERT INTO clientes (nome) VALUES (?)", (cliente.nome,)
            )
        return registro.lastrowid

    def cadastrar_equipe(self, equipe: Equipe) -> int:
        with self.conexao:
            registro = self.conexao.execute(
                "INSERT INTO equipes (nome) VALUES (?)", (equipe.nome,)
            )
        return registro.lastrowid

    def listar_clientes(self) -> dict[int, Cliente]:
        registros = self.conexao.execute("SELECT id, nome FROM clientes ORDER BY id")
        return {numero: Cliente(nome) for numero, nome in registros}

    def listar_equipes(self) -> dict[int, Equipe]:
        registros = self.conexao.execute("SELECT id, nome FROM equipes ORDER BY id")
        return {numero: Equipe(nome) for numero, nome in registros}

    def abrir_ordem(self, cliente_id: int, equipe_id: int, tipo: int) -> int:
        _, classe_servico = TIPOS_SERVICO[tipo]
        etapas = classe_servico().gerar_checklist()
        with self.conexao:
            registro = self.conexao.execute(
                "INSERT INTO ordens (cliente_id, equipe_id, tipo) VALUES (?, ?, ?)",
                (cliente_id, equipe_id, tipo),
            )
            numero = registro.lastrowid
            self.conexao.executemany(
                "INSERT INTO itens_checklist (ordem_numero, numero, descricao) VALUES (?, ?, ?)",
                ((numero, posicao, etapa) for posicao, etapa in enumerate(etapas, start=1)),
            )
        return numero

    def listar_ordens(self) -> dict[int, OrdemServico]:
        registros = self.conexao.execute("""
            SELECT o.numero, o.tipo, o.concluida, c.nome, e.nome, i.descricao, i.concluido
            FROM ordens AS o
            JOIN clientes AS c ON c.id = o.cliente_id
            JOIN equipes AS e ON e.id = o.equipe_id
            JOIN itens_checklist AS i ON i.ordem_numero = o.numero
            ORDER BY o.numero, i.numero
        """)
        ordens = {}
        for numero, linhas_da_ordem in groupby(registros, key=lambda linha: linha[0]):
            linhas = list(linhas_da_ordem)
            _, tipo, concluida, cliente, equipe, _, _ = linhas[0]
            _, classe_servico = TIPOS_SERVICO[tipo]
            ordem = OrdemServico(
                numero,
                Cliente(cliente),
                Equipe(equipe),
                classe_servico(),
                itens=(ItemChecklist(descricao, bool(ok)) for *_, descricao, ok in linhas),
            )
            if concluida:
                ordem.concluir()
            ordens[numero] = ordem
        return ordens

    def marcar_etapa(self, ordem: OrdemServico, numero_etapa: int) -> None:
        ordem.marcar_etapa(numero_etapa)
        with self.conexao:
            self.conexao.execute(
                "UPDATE itens_checklist SET concluido = 1 WHERE ordem_numero = ? AND numero = ?",
                (ordem.numero, numero_etapa),
            )

    def concluir_ordem(self, ordem: OrdemServico) -> None:
        ordem.concluir()
        with self.conexao:
            self.conexao.execute(
                "UPDATE ordens SET concluida = 1 WHERE numero = ?", (ordem.numero,)
            )
