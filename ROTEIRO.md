# JAM-DF | Roteiro do Desk App II

A duração prevista é de **5 minutos e 30 segundos**, com 30 segundos de margem.
Abram o terminal na pasta do projeto e usem os dados fictícios abaixo.
Iniciem uma sessão nova para que os números coincidam com o roteiro.

## Pessoa 1 — Menu, cadastros e abertura de ordens (0:00–2:40)

**0:00–0:40 · Apresentação.** Execute `python main.py` e mostre o menu.

> Olá! Este é o JAM-DF, um aplicativo em Python para organizar os serviços de
> uma empresa de segurança eletrônica. No nível 2, o menu permite cadastrar
> clientes e equipes, acompanhar ordens e consultar um relatório. Vamos mostrar
> como uma ordem passa da abertura à conclusão.

**0:40–1:25 · Cadastros.** Na opção **1**, cadastre **Comércio Horizonte**. Na
opção **3**, cadastre **Equipe Técnica**. Mostre os dois registros com as opções
**2** e **4**.

> Primeiro, vou cadastrar um cliente e uma equipe. Cada um recebeu o número 1
> na sua lista, e podemos usar os mesmos registros em várias ordens.

**1:25–2:40 · Serviços e ordens.** Na opção **10**, mostre os tipos de serviço e
suas etapas. Use a opção **5** duas vezes. Informe o cliente **1** e a equipe **1**
em ambas. Escolha o tipo **1** na primeira e o tipo **2** na segunda.

> A empresa oferece instalação, manutenção e consultoria. Cada tipo tem seu
> próprio checklist. Vou abrir uma ordem de instalação e outra de manutenção
> para o mesmo cliente e a mesma equipe. Agora vamos acompanhar a instalação.

## Pessoa 2 — Checklist, conclusão e relatório (2:40–5:30)

**2:40–3:25 · Checklists.** Abra a opção **6**. Aponte para o status, o cliente,
a equipe e as etapas pendentes de cada ordem.

> As duas ordens estão abertas. Na instalação, temos que instalar os
> equipamentos e testar o funcionamento. Na manutenção, a primeira etapa é
> diagnosticar a falha. O tipo de serviço define as etapas de cada ordem.

**3:25–4:40 · Regra de conclusão.** Na opção **7**, informe a ordem **1** e
marque a etapa **1**. Na opção **8**, tente concluir a ordem **1** e mostre a
mensagem. Volte à opção **7**, marque a etapa **2** da ordem **1** e finalize
pela opção **8**. Use a opção **6** para mostrar o novo status.

> Marquei a primeira etapa e vou tentar concluir a ordem. O sistema avisa
> que ainda há uma etapa pendente. Depois de marcar a segunda etapa, consigo
> concluir a instalação. A manutenção continua aberta.

**4:40–5:30 · Relatório e testes.** Abra a opção **9**, mostre os totais e saia
pela opção **0**. No terminal, execute `python -m unittest -v` e mostre o `OK`.

> O relatório mostra uma ordem aberta e uma concluída. Nesta versão, os
> dados ficam em memória durante a execução. Os testes verificam a modelagem
> e o fluxo do menu. O link do repositório está na entrega.
