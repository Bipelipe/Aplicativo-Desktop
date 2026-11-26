"""Interface gráfica do JAM-DF para o Desk App IV."""

import sqlite3
import tkinter as tk
from argparse import ArgumentParser
from contextlib import closing
from pathlib import Path
from tkinter import font, messagebox, ttk

from banco import BANCO_PADRAO, BancoDados
from modelos import Cliente, Equipe, RelatorioServicos, TIPOS_SERVICO


FUNDO = "#edf3f6"
PAINEL = "#ffffff"
NAV = "#10263b"
NAV_ATIVO = "#1c4157"
TEXTO = "#122b3e"
TEXTO_SUAVE = "#4b6473"
ACENTO = "#09645e"
ACENTO_HOVER = "#07534e"
LINHA = "#dbe5ea"


def configurar_tema(root: tk.Tk) -> None:
    root.configure(background=FUNDO)
    familia = font.nametofont("TkDefaultFont", root=root).actual("family")
    tema = ttk.Style(root)
    tema.theme_use("clam")
    tema.configure(".", background=FUNDO, foreground=TEXTO, font=(familia, 11))
    tema.configure("Painel.TFrame", background=PAINEL)
    tema.configure("Nav.TFrame", background=NAV)
    tema.configure("TLabel", background=FUNDO, foreground=TEXTO)
    tema.configure("Marca.TLabel", background=NAV, foreground=PAINEL, font=(familia, 23, "bold"))
    tema.configure("Titulo.TLabel", font=(familia, 23, "bold"))
    tema.configure("Painel.TLabel", background=PAINEL)
    tema.configure("Secao.TLabel", background=PAINEL, font=(familia, 13, "bold"))
    tema.configure("TextoPainel.TLabel", background=PAINEL, foreground=TEXTO_SUAVE)
    tema.configure("Indicador.TLabel", background=PAINEL, foreground=ACENTO, font=(familia, 25, "bold"))
    tema.configure("Rodape.TLabel", foreground=TEXTO_SUAVE)

    tema.configure(
        "TButton", padding=(12, 7), background=PAINEL, bordercolor=LINHA,
        lightcolor=PAINEL, darkcolor=PAINEL,
    )
    tema.map("TButton", background=[("active", "#e0eeed")])
    tema.configure(
        "Acao.TButton", background=ACENTO, foreground=PAINEL, bordercolor=ACENTO,
        lightcolor=ACENTO, darkcolor=ACENTO,
    )
    tema.map(
        "Acao.TButton",
        background=[("disabled", LINHA), ("active", ACENTO_HOVER)],
        foreground=[("disabled", TEXTO_SUAVE)],
    )
    tema.configure(
        "Nav.TButton", anchor="w", padding=(12, 10), background=NAV,
        foreground=PAINEL, bordercolor=NAV, lightcolor=NAV, darkcolor=NAV,
    )
    tema.map("Nav.TButton", background=[("active", NAV_ATIVO)])
    tema.configure("NavAtiva.TButton", **tema.configure("Nav.TButton"))
    tema.configure("NavAtiva.TButton", background=NAV_ATIVO, bordercolor=NAV_ATIVO)
    tema.map("NavAtiva.TButton", background=[("active", NAV_ATIVO)])

    tema.configure("Treeview", background=PAINEL, fieldbackground=PAINEL, rowheight=31, bordercolor=LINHA)
    tema.configure(
        "Treeview.Heading", background="#e5eef2", font=(familia, 10, "bold"),
        padding=(8, 6), bordercolor=LINHA, lightcolor="#e5eef2", darkcolor="#e5eef2",
    )
    tema.configure(
        "Vertical.TScrollbar", background=LINHA, troughcolor=PAINEL, bordercolor=LINHA,
        lightcolor=LINHA, darkcolor=LINHA, arrowcolor=TEXTO_SUAVE, gripcount=0,
    )
    tema.map("Treeview", background=[("selected", "#cce8e5")], foreground=[("selected", TEXTO)])
    tema.configure("TEntry", fieldbackground=PAINEL, padding=6, bordercolor=LINHA)
    tema.configure("TCombobox", padding=6, bordercolor=LINHA)
    tema.map(
        "TEntry", selectbackground=[("focus", "#cce8e5")], selectforeground=[("focus", TEXTO)],
    )
    tema.map(
        "TCombobox", fieldbackground=[("readonly", PAINEL)],
        selectbackground=[("focus", "#cce8e5")], selectforeground=[("focus", TEXTO)],
    )


def criar_tabela(pai, colunas, altura: int = 7) -> ttk.Treeview:
    moldura = ttk.Frame(pai, style="Painel.TFrame")
    moldura.pack(fill="both", expand=True)
    tabela = ttk.Treeview(
        moldura, columns=[coluna[0] for coluna in colunas],
        show="headings", selectmode="browse", height=altura,
    )
    for chave, titulo, largura, flexivel in colunas:
        tabela.heading(chave, text=titulo)
        tabela.column(chave, width=largura, minwidth=largura, stretch=flexivel)
    rolagem = ttk.Scrollbar(moldura, orient="vertical", command=tabela.yview)
    tabela.configure(yscrollcommand=rolagem.set)
    tabela.pack(side="left", fill="both", expand=True)
    rolagem.pack(side="right", fill="y")
    return tabela


class Aplicativo:
    def __init__(self, root: tk.Tk, banco: BancoDados):
        self.root = root
        self.banco = banco
        self.relatorio = RelatorioServicos()
        self.nomes_servicos = {classe: nome for nome, classe in TIPOS_SERVICO.values()}
        self.root.title("JAM-DF | Desk App IV")
        self.root.geometry("1100x680")
        self.root.minsize(940, 560)
        configurar_tema(root)

        lateral = ttk.Frame(root, padding=(16, 25), style="Nav.TFrame")
        lateral.pack(side="left", fill="y")
        ttk.Label(lateral, text="JAM-DF", style="Marca.TLabel").pack(anchor="w", pady=(0, 26))
        paginas = {
            "Ordens de serviço": self.mostrar_ordens,
            "Clientes": lambda: self.mostrar_cadastros("Clientes"),
            "Equipes": lambda: self.mostrar_cadastros("Equipes"),
            "Tipos de serviço": self.mostrar_tipos,
        }
        self.navegacao = {}
        for nome, abrir in paginas.items():
            botao = ttk.Button(lateral, text=nome, command=abrir, style="Nav.TButton")
            botao.pack(fill="x", pady=3)
            self.navegacao[nome] = botao

        area = ttk.Frame(root, padding=(24, 18, 24, 12))
        area.pack(side="left", fill="both", expand=True)
        self.pagina = ttk.Frame(area)
        self.pagina.pack(fill="both", expand=True)
        self.mensagem = tk.StringVar(root, value="")
        ttk.Label(area, textvariable=self.mensagem, style="Rodape.TLabel").pack(
            anchor="w", pady=(10, 0)
        )
        self.mostrar_ordens()

    def preparar_pagina(self, nome: str) -> ttk.Frame:
        for filho in self.pagina.winfo_children():
            filho.destroy()
        for pagina, botao in self.navegacao.items():
            botao.configure(style="NavAtiva.TButton" if pagina == nome else "Nav.TButton")
        self.mensagem.set("")
        cabecalho = ttk.Frame(self.pagina)
        cabecalho.pack(fill="x", pady=(0, 14))
        ttk.Label(cabecalho, text=nome, style="Titulo.TLabel").pack(side="left")
        return cabecalho

    def mostrar_ordens(self, numero: int | None = None) -> None:
        self.ordens = self.banco.listar_ordens()
        resumo = self.relatorio.resumir(self.ordens.values())
        cabecalho = self.preparar_pagina("Ordens de serviço")
        ttk.Button(cabecalho, text="Nova ordem", command=self.janela_ordem, style="Acao.TButton").pack(
            side="right", pady=3
        )
        indicadores = ttk.Frame(self.pagina)
        indicadores.pack(fill="x", pady=(0, 12))
        for posicao, (rotulo, total) in enumerate((
            ("Abertas", resumo["abertas"]), ("Concluídas", resumo["concluidas"]),
        )):
            painel = ttk.Frame(indicadores, style="Painel.TFrame", padding=(14, 7))
            painel.grid(row=0, column=posicao, sticky="ew", padx=(0, 8) if posicao == 0 else (8, 0))
            indicadores.columnconfigure(posicao, weight=1, uniform="totais")
            ttk.Label(painel, text=rotulo, style="TextoPainel.TLabel").pack(anchor="w")
            ttk.Label(painel, text=str(total), style="Indicador.TLabel").pack(anchor="w")

        paineis = ttk.Frame(self.pagina)
        paineis.pack(fill="both", expand=True)
        paineis.rowconfigure(0, weight=1)
        paineis.columnconfigure(0, weight=1, uniform="ordens")
        paineis.columnconfigure(1, weight=1, uniform="ordens")

        lista = ttk.Frame(paineis, style="Painel.TFrame", padding=12)
        lista.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        ttk.Label(lista, text="Ordens registradas", style="Secao.TLabel").pack(anchor="w", pady=(0, 9))
        self.tabela_ordens = criar_tabela(lista, (
            ("numero", "OS", 38, False), ("tipo", "Serviço", 101, True),
            ("status", "Status", 95, False),
        ))
        for ordem in self.ordens.values():
            self.tabela_ordens.insert("", "end", iid=str(ordem.numero), values=(
                f"#{ordem.numero}", self.nomes_servicos[type(ordem.servico)],
                "Concluída" if ordem.concluida else "Aberta",
            ))
        self.tabela_ordens.bind("<<TreeviewSelect>>", self.atualizar_detalhes)
        if not self.ordens:
            ttk.Label(lista, text="Nenhuma ordem cadastrada.", style="TextoPainel.TLabel").pack(
                anchor="w", pady=(8, 0)
            )

        self.detalhes = ttk.Frame(paineis, style="Painel.TFrame", padding=12)
        self.detalhes.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        if self.ordens:
            selecionada = str(numero if numero in self.ordens else next(iter(self.ordens)))
            self.tabela_ordens.selection_set(selecionada)
            self.tabela_ordens.focus(selecionada)
            self.tabela_ordens.see(selecionada)
        else:
            self.atualizar_detalhes()

    def atualizar_detalhes(self, _evento=None) -> None:
        for filho in self.detalhes.winfo_children():
            filho.destroy()
        selecao = self.tabela_ordens.selection()
        if not selecao:
            ttk.Label(self.detalhes, text="Checklist da ordem", style="Secao.TLabel").pack(anchor="w")
            ttk.Label(
                self.detalhes, text="Selecione uma ordem para ver as etapas.", style="TextoPainel.TLabel",
            ).pack(anchor="w", pady=(8, 0))
            return

        ordem = self.ordens[int(selecao[0])]
        ttk.Label(self.detalhes, text=f"Checklist · OS {ordem.numero}", style="Secao.TLabel").pack(anchor="w")
        for rotulo, nome in (("Cliente", ordem.cliente.nome), ("Equipe", ordem.equipe.nome)):
            ttk.Label(
                self.detalhes, text=f"{rotulo}: {nome}", wraplength=275, style="TextoPainel.TLabel",
            ).pack(anchor="w", pady=(3, 0))

        corpo = ttk.Frame(self.detalhes, style="Painel.TFrame")
        corpo.pack(fill="x", pady=(8, 0))
        self.tabela_etapas = criar_tabela(corpo, (
            ("etapa", "Etapa", 160, True), ("status", "Situação", 82, False),
        ), altura=3)
        for numero, item in enumerate(ordem.itens, start=1):
            self.tabela_etapas.insert("", "end", iid=str(numero), values=(
                item.descricao, "Marcada" if item.concluido else "Pendente",
            ))

        acoes = ttk.Frame(self.detalhes, style="Painel.TFrame")
        acoes.pack(fill="x", pady=(9, 0))
        marcar = ttk.Button(acoes, text="Marcar etapa", command=lambda: self.marcar_etapa(ordem))
        marcar.pack(side="left")
        marcar.state(["disabled"])
        self.tabela_etapas.bind("<<TreeviewSelect>>", lambda evento: self.habilitar_etapa(marcar, ordem))
        concluir = ttk.Button(
            acoes, text="Concluir ordem", style="Acao.TButton", command=lambda: self.concluir_ordem(ordem),
        )
        concluir.pack(side="right")
        if ordem.concluida:
            concluir.state(["disabled"])

    def habilitar_etapa(self, botao, ordem) -> None:
        selecao = self.tabela_etapas.selection()
        if selecao and not ordem.itens[int(selecao[0]) - 1].concluido:
            botao.state(["!disabled"])
        else:
            botao.state(["disabled"])

    def marcar_etapa(self, ordem) -> None:
        numero = int(self.tabela_etapas.selection()[0])
        try:
            self.banco.marcar_etapa(ordem, numero)
        except sqlite3.Error as erro:
            messagebox.showerror("Banco de dados", str(erro), parent=self.root)
            return
        self.mostrar_ordens(ordem.numero)
        self.mensagem.set(f"Etapa {numero} da OS {ordem.numero} marcada.")

    def concluir_ordem(self, ordem) -> None:
        try:
            self.banco.concluir_ordem(ordem)
        except ValueError as erro:
            messagebox.showwarning("Etapas pendentes", str(erro), parent=self.root)
            return
        except sqlite3.Error as erro:
            messagebox.showerror("Banco de dados", str(erro), parent=self.root)
            return
        self.mostrar_ordens(ordem.numero)
        self.mensagem.set(f"OS {ordem.numero} concluída.")

    def mostrar_cadastros(self, categoria: str) -> None:
        cliente = categoria == "Clientes"
        registros = self.banco.listar_clientes() if cliente else self.banco.listar_equipes()
        cabecalho = self.preparar_pagina(categoria)
        ttk.Button(
            cabecalho, text="Novo cliente" if cliente else "Nova equipe",
            command=lambda: self.janela_cadastro(categoria), style="Acao.TButton",
        ).pack(side="right", pady=3)
        painel = ttk.Frame(self.pagina, style="Painel.TFrame", padding=12)
        painel.pack(fill="both", expand=True)
        tabela = criar_tabela(painel, (
            ("numero", "Nº", 54, False), ("nome", "Nome", 210, True),
        ))
        for numero, registro in registros.items():
            tabela.insert("", "end", values=(numero, registro.nome))
        if not registros:
            ttk.Label(painel, text="Nenhum registro cadastrado.", style="TextoPainel.TLabel").pack(
                anchor="w", pady=(8, 0)
            )

    def mostrar_tipos(self) -> None:
        self.preparar_pagina("Tipos de serviço")
        for nome, classe in TIPOS_SERVICO.values():
            painel = ttk.Frame(self.pagina, style="Painel.TFrame", padding=(14, 9))
            painel.pack(fill="x", pady=(0, 10))
            ttk.Label(painel, text=nome, style="Secao.TLabel").pack(anchor="w", pady=(0, 4))
            for numero, etapa in enumerate(classe().gerar_checklist(), start=1):
                ttk.Label(painel, text=f"{numero}. {etapa}", style="TextoPainel.TLabel").pack(anchor="w")

    def criar_janela(self, titulo: str) -> tuple[tk.Toplevel, ttk.Frame]:
        janela = tk.Toplevel(self.root)
        janela.title(titulo)
        janela.transient(self.root)
        janela.resizable(False, False)
        janela.geometry(f"+{self.root.winfo_rootx() + 90}+{self.root.winfo_rooty() + 70}")
        janela.bind("<Escape>", lambda _evento: janela.destroy())
        painel = ttk.Frame(janela, padding=20)
        painel.pack(fill="both", expand=True)
        janela.grab_set()
        return janela, painel

    def janela_cadastro(self, categoria: str) -> None:
        cliente = categoria == "Clientes"
        janela, painel = self.criar_janela("Novo cliente" if cliente else "Nova equipe")
        ttk.Label(painel, text="Nome do cliente" if cliente else "Nome da equipe").pack(anchor="w")
        entrada = ttk.Entry(painel, width=36)
        entrada.pack(fill="x", pady=(4, 12))

        def salvar(_evento=None):
            nome = entrada.get().strip()
            if not nome:
                messagebox.showwarning("Nome obrigatório", "Informe um nome.", parent=janela)
                return
            try:
                if cliente:
                    numero = self.banco.cadastrar_cliente(Cliente(nome))
                else:
                    numero = self.banco.cadastrar_equipe(Equipe(nome))
            except sqlite3.Error as erro:
                messagebox.showerror("Banco de dados", str(erro), parent=janela)
                return
            janela.destroy()
            self.mostrar_cadastros(categoria)
            registro = "Cliente" if cliente else "Equipe"
            self.mensagem.set(f"{registro} {numero} — {nome}.")

        ttk.Button(painel, text="Salvar", command=salvar, style="Acao.TButton").pack(anchor="e")
        janela.bind("<Return>", salvar)
        entrada.focus_set()

    def janela_ordem(self) -> None:
        clientes = self.banco.listar_clientes()
        equipes = self.banco.listar_equipes()
        if not clientes or not equipes:
            messagebox.showwarning(
                "Cadastros necessários", "Cadastre um cliente e uma equipe antes de abrir uma ordem.",
                parent=self.root,
            )
            return
        janela, painel = self.criar_janela("Nova ordem")
        campos = (
            ("Cliente", [f"{numero}. {cliente.nome}" for numero, cliente in clientes.items()]),
            ("Equipe", [f"{numero}. {equipe.nome}" for numero, equipe in equipes.items()]),
            ("Tipo de serviço", [nome for nome, _classe in TIPOS_SERVICO.values()]),
        )
        seletores = []
        for rotulo, valores in campos:
            ttk.Label(painel, text=rotulo).pack(anchor="w")
            seletor = ttk.Combobox(painel, values=valores, state="readonly", width=34)
            seletor.current(0)
            seletor.pack(fill="x", pady=(3, 10))
            seletores.append(seletor)

        def salvar():
            cliente_id = list(clientes)[seletores[0].current()]
            equipe_id = list(equipes)[seletores[1].current()]
            tipo = list(TIPOS_SERVICO)[seletores[2].current()]
            try:
                numero = self.banco.abrir_ordem(cliente_id, equipe_id, tipo)
            except sqlite3.Error as erro:
                messagebox.showerror("Banco de dados", str(erro), parent=janela)
                return
            janela.destroy()
            self.mostrar_ordens(numero)
            self.mensagem.set(f"OS {numero} aberta.")

        ttk.Button(painel, text="Abrir ordem", command=salvar, style="Acao.TButton").pack(anchor="e")
        seletores[0].focus_set()


def main() -> None:
    argumentos = ArgumentParser(description="JAM-DF | Desk App IV")
    argumentos.add_argument(
        "--banco", type=Path, default=BANCO_PADRAO, help="Arquivo SQLite a usar.",
    )
    caminho = argumentos.parse_args().banco
    try:
        root = tk.Tk()
    except tk.TclError as erro:
        argumentos.exit(1, f"Erro ao abrir a interface gráfica: {erro}\n")

    try:
        with closing(sqlite3.connect(caminho)) as conexao:
            Aplicativo(root, BancoDados(conexao))
            root.mainloop()
    except sqlite3.Error as erro:
        root.destroy()
        argumentos.exit(1, f"Erro ao abrir o banco de dados: {erro}\n")


if __name__ == "__main__":
    main()
