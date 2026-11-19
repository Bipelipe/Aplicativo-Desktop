import unittest

from modelos import (
    Cliente, Consultoria, Equipe, Instalacao, Manutencao, OrdemServico,
    RelatorioServicos, Servico,
)


class TestOrdemServico(unittest.TestCase):
    def setUp(self):
        self.cliente = Cliente("Comércio Horizonte")
        self.equipe = Equipe("Equipe Técnica")
        self.ordem = OrdemServico(1, self.cliente, self.equipe, Instalacao())

    def test_associacoes_com_cliente_e_equipe(self):
        segunda = OrdemServico(2, self.cliente, self.equipe, Consultoria())
        self.assertIs(self.ordem.cliente, segunda.cliente)
        self.assertIs(self.ordem.equipe, segunda.equipe)
        self.assertEqual(self.cliente.nome, "Comércio Horizonte")
        self.assertEqual(self.equipe.nome, "Equipe Técnica")

    def test_checklist_polimorfico(self):
        casos = (
            (Instalacao(), ("Instalar equipamentos", "Testar funcionamento")),
            (Manutencao(), ("Diagnosticar falha", "Testar após o reparo")),
            (Consultoria(), ("Levantar necessidades", "Apresentar recomendações")),
        )
        for servico, esperado in casos:
            with self.subTest(servico=type(servico).__name__):
                self.assertIsInstance(servico, Servico)
                ordem = OrdemServico(2, self.cliente, self.equipe, servico)
                self.assertEqual(tuple(item.descricao for item in ordem.itens), esperado)
                self.assertFalse(any(item.concluido for item in ordem.itens))

    def test_itens_pertencem_a_cada_ordem(self):
        segunda = OrdemServico(2, self.cliente, self.equipe, self.ordem.servico)
        self.assertIsNot(self.ordem.itens[0], segunda.itens[0])
        self.ordem.marcar_etapa(1)
        self.assertTrue(self.ordem.itens[0].concluido)
        self.assertFalse(segunda.itens[0].concluido)

    def test_rejeita_numero_de_etapa_invalido(self):
        for numero in (0, -1, 3):
            with self.subTest(numero=numero), self.assertRaises(ValueError):
                self.ordem.marcar_etapa(numero)
        self.assertFalse(any(item.concluido for item in self.ordem.itens))

    def test_conclusao_exige_todas_as_etapas(self):
        self.ordem.marcar_etapa(1)
        with self.assertRaisesRegex(ValueError, "todas as etapas"):
            self.ordem.concluir()
        self.assertFalse(self.ordem.concluida)
        self.ordem.marcar_etapa(2)
        self.ordem.concluir()
        self.assertTrue(self.ordem.concluida)

    def test_relatorio_por_status(self):
        terminada = OrdemServico(2, self.cliente, self.equipe, Consultoria())
        terminada.marcar_etapa(1)
        terminada.marcar_etapa(2)
        terminada.concluir()
        relatorio = RelatorioServicos()
        self.assertEqual(
            relatorio.resumir([self.ordem, terminada]), {"abertas": 1, "concluidas": 1}
        )
        self.assertEqual(relatorio.resumir([]), {"abertas": 0, "concluidas": 0})
