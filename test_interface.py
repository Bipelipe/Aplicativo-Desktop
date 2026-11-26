import sqlite3
import unittest
from unittest.mock import patch

from banco import BancoDados

try:
    import tkinter as tk
    from tkinter import ttk
except ImportError:
    tk = None
else:
    from interface import Aplicativo


def percorrer_widgets(pai):
    for widget in pai.winfo_children():
        yield widget
        yield from percorrer_widgets(widget)


@unittest.skipIf(tk is None, "Tkinter indisponível")
class TestInterface(unittest.TestCase):
    def setUp(self):
        try:
            self.janela = tk.Tk()
        except tk.TclError as erro:
            self.skipTest(f"Interface gráfica indisponível: {erro}")

        conexao = sqlite3.connect(":memory:")
        self.addCleanup(conexao.close)
        self.addCleanup(self.janela.destroy)
        self.banco = BancoDados(conexao)
        self.aplicativo = Aplicativo(self.janela, self.banco)
        self.janela.update()

    def buscar_widget(self, pai, classe, texto=None):
        for widget in percorrer_widgets(pai):
            if isinstance(widget, classe) and (texto is None or widget.cget("text") == texto):
                return widget
        self.fail(f"Widget {classe} {texto or ''} ausente.")

    def clicar(self, texto, pai=None):
        botao = self.buscar_widget(pai or self.janela, (tk.Button, ttk.Button), texto)
        botao.invoke()
        self.janela.update()

    def cadastrar(self, pagina, botao, nome):
        self.clicar(pagina)
        self.clicar(botao)
        formulario = self.buscar_widget(self.janela, tk.Toplevel)
        campo = self.buscar_widget(formulario, ttk.Entry)
        campo.insert(0, nome)
        self.clicar("Salvar", formulario)

    @patch("tkinter.messagebox.showwarning")
    def test_fluxo_de_ordem_de_servico(self, aviso):
        self.cadastrar("Clientes", "Novo cliente", "Mercado São José")
        self.cadastrar("Equipes", "Nova equipe", "Equipe Técnica")
        self.assertEqual(self.banco.listar_clientes()[1].nome, "Mercado São José")
        self.assertEqual(self.banco.listar_equipes()[1].nome, "Equipe Técnica")

        self.clicar("Tipos de serviço")
        for etapa in ("Instalar equipamentos", "Diagnosticar falha", "Levantar necessidades"):
            self.buscar_widget(self.janela, ttk.Label, f"1. {etapa}")

        self.clicar("Ordens de serviço")
        self.clicar("Nova ordem")
        formulario = self.buscar_widget(self.janela, tk.Toplevel)
        campos = [
            widget for widget in percorrer_widgets(formulario) if isinstance(widget, ttk.Combobox)
        ]
        self.assertEqual(len(campos), 3)
        for campo in campos:
            campo.current(0)
        self.clicar("Abrir ordem", formulario)
        ordem = self.banco.listar_ordens()[1]
        self.assertEqual(ordem.cliente.nome, "Mercado São José")
        self.assertEqual(ordem.equipe.nome, "Equipe Técnica")
        self.assertEqual(ordem.itens[0].descricao, "Instalar equipamentos")

        self.aplicativo.tabela_ordens.selection_set("1")
        self.janela.update()
        self.clicar("Concluir ordem")
        aviso.assert_called_once()
        self.assertIn("todas as etapas", aviso.call_args.args[1])
        self.assertFalse(self.banco.listar_ordens()[1].concluida)

        for numero in ("1", "2"):
            self.aplicativo.tabela_ordens.selection_set("1")
            self.janela.update()
            self.aplicativo.tabela_etapas.selection_set(numero)
            self.janela.update()
            self.clicar("Marcar etapa")
            self.assertTrue(self.banco.listar_ordens()[1].itens[int(numero) - 1].concluido)

        self.aplicativo.tabela_ordens.selection_set("1")
        self.janela.update()
        self.clicar("Concluir ordem")
        self.assertTrue(self.banco.listar_ordens()[1].concluida)
        self.assertEqual(self.aplicativo.tabela_ordens.set("1", "status"), "Concluída")
        for rotulo, total in (("Abertas", "0"), ("Concluídas", "1")):
            cartao = self.buscar_widget(self.janela, ttk.Label, rotulo).master
            self.buscar_widget(cartao, ttk.Label, total)


if __name__ == "__main__":
    unittest.main()
