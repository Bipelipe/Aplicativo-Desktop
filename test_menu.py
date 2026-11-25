import subprocess
import sys
import unittest
from pathlib import Path


class TestMenu(unittest.TestCase):
    def executar_menu(self, *entradas: str) -> str:
        resultado = subprocess.run(
            [sys.executable, "-X", "utf8", "main.py"],
            cwd=Path(__file__).resolve().parent,
            input="\n".join((*entradas, "")),
            encoding="utf-8",
            capture_output=True,
            timeout=10,
        )
        self.assertEqual(resultado.returncode, 0, resultado.stderr)
        return resultado.stdout

    def test_fluxo_completo_pelo_menu(self):
        saida = self.executar_menu(
            "1", "Mercado Horizonte",
            "2",
            "3", "Equipe Alfa",
            "4",
            "5", "1", "1", "1",
            "5", "1", "1", "2",
            "5", "1", "1", "3",
            "6",
            "8", "1",
            "7", "1", "1",
            "7", "1", "2",
            "8", "1",
            "6",
            "9",
            "0",
        )
        self.assertIn("Clientes\n1. Mercado Horizonte", saida)
        self.assertIn("Equipes\n1. Equipe Alfa", saida)
        self.assertIn("OS 1 | Instalação | Aberta", saida)
        self.assertIn("OS 1 | Instalação | Concluída", saida)
        self.assertIn("OS 2 | Manutenção | Aberta", saida)
        self.assertIn("OS 3 | Consultoria | Aberta", saida)
        self.assertIn("1. [x] Instalar equipamentos", saida)
        self.assertIn("2. [x] Testar funcionamento", saida)
        self.assertIn("1. [ ] Diagnosticar falha", saida)
        self.assertIn("1. [ ] Levantar necessidades", saida)
        self.assertIn("Conclua todas as etapas primeiro.", saida)
        self.assertIn("Abertas: 2 | Concluídas: 1", saida)
        self.assertTrue(saida.endswith("JAM-DF encerrado.\n"))

    def test_consulta_checklists_dos_tipos_de_servico(self):
        saida = self.executar_menu("10", "0")
        self.assertIn("Instalar equipamentos", saida)
        self.assertIn("Diagnosticar falha", saida)
        self.assertIn("Levantar necessidades", saida)

    def test_entradas_invalidas_preservam_os_dados(self):
        saida = self.executar_menu(
            "99",
            "5",
            "1", " ",
            "1", "Mercado Horizonte",
            "3", "Equipe Alfa",
            "5", "texto",
            "5", "2",
            "5", "1", "1", "4",
            "5", "1", "1", "1",
            "7", "2",
            "7", "1", "0",
            "6",
            "9",
            "0",
        )
        self.assertIn("Opção inválida.", saida)
        self.assertIn("Cadastre um cliente e uma equipe", saida)
        self.assertIn("Informe um nome.", saida)
        self.assertIn("Digite um número válido.", saida)
        self.assertEqual(saida.count("Número não encontrado."), 4)
        self.assertIn("1. [ ] Instalar equipamentos", saida)
        self.assertIn("Abertas: 1 | Concluídas: 0", saida)

    def test_nova_sessao_comeca_vazia_e_encerra_no_fim_da_entrada(self):
        self.executar_menu("1", "Mercado Horizonte", "0")
        saida = self.executar_menu("2", "4", "6", "9")
        self.assertEqual(saida.count("Nenhum registro cadastrado."), 2)
        self.assertIn("Nenhuma ordem cadastrada.", saida)
        self.assertIn("Abertas: 0 | Concluídas: 0", saida)
        self.assertTrue(saida.endswith("JAM-DF encerrado.\n"))


if __name__ == "__main__":
    unittest.main()
