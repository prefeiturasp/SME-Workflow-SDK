# SME-Workflow-SDK

[![python](https://img.shields.io/badge/python-3.12-blue.svg)]()
[![license](https://img.shields.io/badge/license-AGPL--3.0-green.svg)]()

## Objetivo e escopo

O **SME-Workflow-SDK** é uma biblioteca Python para gerenciamento de workflows configuráveis, responsável por validar ações e controlar transições entre estados de um processo.

A biblioteca utiliza arquivos YAML para declarar os estados, as ações disponíveis e as transições permitidas, reduzindo o acoplamento entre as regras do fluxo e o código das aplicações consumidoras.

O SDK é independente do domínio de negócio e pode ser utilizado em aplicações Python, incluindo sistemas desenvolvidos com Django.

### Responsabilidades do SDK

- Carregar e validar configurações de workflow em YAML.
- Verificar se uma ação está disponível no estado atual.
- Validar a transição configurada e seu estado de destino.
- Identificar transições terminais.
- Produzir um resultado estruturado da execução, incluindo estados, ação, horários, contexto e status.

### Responsabilidades da aplicação consumidora

- Executar as regras de negócio relacionadas à ação solicitada.
- Controlar a persistência do estado atual e do histórico do processo.
- Gerenciar permissões de usuários e regras específicas do domínio.
- Realizar auditoria, notificações e demais efeitos externos, quando aplicáveis.

O SDK não executa regras de negócio específicas da aplicação nem persiste alterações no processo.

## Funcionalidades

- Configuração declarativa de workflows por YAML.
- Validação estrutural e semântica da configuração.
- Validação de estados e ações disponíveis.
- Resolução e validação de transições.
- Tratamento de exceções específicas para configuração e execução.
- Contexto de execução com identificador, autor e dados adicionais.
- Resultado estruturado com informações da transição e horários.
- Separação entre gerenciamento do workflow e regras de negócio.

## Instalação e configuração

### Pré-requisitos

- Python 3.12 ou superior.
- Git, para instalação diretamente do repositório.
- Acesso ao repositório do projeto.

### Instalação

Instale o SDK diretamente do GitHub:

```bash
pip install git+https://github.com/prefeiturasp/SME-Workflow-SDK.git
```

Para instalar uma branch específica, utilize:

```bash
pip install git+https://github.com/prefeiturasp/SME-Workflow-SDK.git@NOME_DA_BRANCH
```

Substitua `NOME_DA_BRANCH` pelo nome da branch desejada.

## Configuração do workflow

O fluxo é declarado em um arquivo YAML. Cada estado possui um campo `acoes`, que define as ações disponíveis e seus respectivos destinos.

```yaml
estados:
  pendente:
    acoes:
      aprovar:
        proximo_estado: aprovado
        terminal: true
      encaminhar:
        proximo_estado: em_analise
        terminal: false

  em_analise:
    acoes:
      concluir:
        proximo_estado: concluido
        terminal: true

  aprovado:
    acoes: null

  concluido:
    acoes: null
```

### Estrutura da configuração

| Campo | Descrição |
|---|---|
| `estados` | Define os estados disponíveis no workflow. |
| `acoes` | Define as ações permitidas para um estado. |
| `proximo_estado` | Informa o estado de destino da ação. |
| `terminal` | Indica se a transição encerra o fluxo. |

O campo `terminal` deve receber um valor booleano (`true` ou `false`).

Um estado com `acoes: null` representa um estado sem ações disponíveis e pode ser utilizado como destino de uma transição terminal.

As transições devem respeitar as regras de consistência: o destino precisa existir, transições terminais devem apontar para estados sem ações e transições não terminais devem apontar para estados com ações configuradas.

## Features

Descrição em breve

## Integração com Django

Descrição em breve

## Desenvolvimento

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev,docs]"
pre-commit install

pytest
pre-commit run --all-files
```

## Documentação viva (Sphinx)

Em breve

## Licença

GNU Affero General Public License v3.0 (AGPL-3.0). Texto completo em
[`LICENSE`](LICENSE).
