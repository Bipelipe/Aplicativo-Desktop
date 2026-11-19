"""Classes do domínio do JAM-DF."""
from abc import ABC, abstractmethod
from collections.abc import Iterable
from dataclasses import dataclass


@dataclass(frozen=True)
class Cliente:
    nome: str


@dataclass(frozen=True)
class Equipe:
    nome: str


class Servico(ABC):
    @abstractmethod
    def gerar_checklist(self) -> tuple[str, ...]:
        """Retorna os nomes das etapas exigidas pelo serviço."""


class Instalacao(Servico):
    def gerar_checklist(self) -> tuple[str, ...]:
        return ("Instalar equipamentos", "Testar funcionamento")


class Manutencao(Servico):
    def gerar_checklist(self) -> tuple[str, ...]:
        return ("Diagnosticar falha", "Testar após o reparo")


class Consultoria(Servico):
    def gerar_checklist(self) -> tuple[str, ...]:
        return ("Levantar necessidades", "Apresentar recomendações")


@dataclass(frozen=True)
class ItemChecklist:
    descricao: str
    concluido: bool = False


class OrdemServico:
    def __init__(self, numero: int, cliente: Cliente, equipe: Equipe, servico: Servico):
        self.numero = numero
        self.cliente = cliente
        self.equipe = equipe
        self.servico = servico
        self._itens = [ItemChecklist(etapa) for etapa in servico.gerar_checklist()]
        self._concluida = False

    @property
    def itens(self) -> tuple[ItemChecklist, ...]:
        return tuple(self._itens)

    @property
    def concluida(self) -> bool:
        return self._concluida

    def marcar_etapa(self, numero_etapa: int) -> None:
        if not 1 <= numero_etapa <= len(self._itens):
            raise ValueError("Número de etapa inválido.")
        indice = numero_etapa - 1
        item = self._itens[indice]
        self._itens[indice] = ItemChecklist(item.descricao, concluido=True)

    def concluir(self) -> None:
        if not all(item.concluido for item in self._itens):
            raise ValueError("Conclua todas as etapas primeiro.")
        self._concluida = True


class RelatorioServicos:
    def resumir(self, ordens: Iterable[OrdemServico]) -> dict[str, int]:
        resumo = {"abertas": 0, "concluidas": 0}
        for ordem in ordens:
            chave = "concluidas" if ordem.concluida else "abertas"
            resumo[chave] += 1
        return resumo
