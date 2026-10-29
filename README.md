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

## Integração com a aplicação

### Carregamento e validação

O `ConfiguradorWorkflow` é o ponto de entrada para carregar e validar o arquivo YAML.

```python
from sme_workflow_sdk import (
    ConfiguradorWorkflow,
    ContextoExecucao,
    MotorWorkflow,
)

configurador = ConfiguradorWorkflow()

configuracao = configurador.carregar("workflow.yaml")
configurador.validar(configuracao)

motor = MotorWorkflow(configuracao)
```

A configuração deve ser validada antes de ser utilizada pelo motor.

### Validação e execução de uma ação

O exemplo abaixo demonstra o fluxo de integração. A aplicação consumidora deve executar sua regra de negócio entre a validação da ação e a produção do resultado.

```python
from sme_workflow_sdk import ContextoExecucao

# Estado atual e ação solicitada.
execucao = motor.validar("pendente", "aprovar")

# A aplicação consumidora executa aqui a regra de negócio
# correspondente à aprovação.

contexto = ContextoExecucao(
    autor="usuario_sistema",
    dados={
        "origem": "aplicacao_consumidora",
    },
)

resultado = motor.executar(execucao, contexto)

if resultado["sucesso"]:
    novo_estado = resultado["proximo_estado"]

    # A aplicação consumidora é responsável por persistir
    # o novo estado e o histórico do processo.
```

**Importante:** a aplicação consumidora deve persistir o novo estado somente após a conclusão bem-sucedida da regra de negócio e conforme as regras transacionais do sistema.

O resultado do motor é um dicionário Python. Os campos de horário continuam sendo objetos `datetime`; portanto, caso seja necessário serializar o resultado em JSON, a aplicação deve definir a conversão desses valores.


## Resultado da execução

O método `MotorWorkflow.executar()` retorna um dicionário com informações sobre a execução.

| Campo | Descrição |
|---|---|
| `identificador` | Identificador da execução. |
| `estado_anterior` | Estado em que a ação foi solicitada. |
| `acao` | Nome da ação executada. |
| `proximo_estado` | Estado de destino da transição. |
| `terminal` | Indica se a transição é terminal. |
| `sucesso` | Indica se o resultado representa uma execução bem-sucedida. |
| `mensagem` | Mensagem descritiva do resultado. |
| `inicio` | Data e hora de início da execução. |
| `fim` | Data e hora de término da execução. |
| `autor` | Identificação do responsável pela execução. |
| `contexto` | Contexto associado à execução. |

## Tratamento de exceções

O SDK define exceções específicas para os problemas encontrados durante a leitura, a validação e o processamento do workflow.

Entre as principais estão:

- `ArquivoNaoEncontradoError`: arquivo de configuração inexistente ou caminho inválido.
- `FormatoInvalidoError`: extensão não suportada, erro de sintaxe YAML ou quantidade inválida de documentos.
- `ConfiguracaoInvalidaError`: conteúdo YAML vazio ou com estrutura de raiz inválida.
- `EstadoInvalidoError`: estado inexistente ou inválido na configuração ou na solicitação.
- `AcaoInvalidaError`: ação indisponível ou malformada.
- `TransicaoInvalidaError`: transição que não atende às regras de validação.
- `ValidacaoDominioError`: dados inválidos nas entidades do domínio.

A aplicação consumidora deve tratar as exceções conforme sua política de erros e garantir que uma operação de negócio não seja considerada concluída quando sua execução falhar.

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
