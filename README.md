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

A aplicação consumidora utiliza o motor de workflow para validar ações e obter os resultados das transições.

### Inicialização

Inicialize o SDK informando o caminho do arquivo YAML:

```python
from sme_workflow_sdk import configure, get_workflow

configure("workflow.yaml")

workflow = get_workflow()
```

### Validação e execução de uma ação

Antes de executar uma ação, a aplicação deve validar se ela está disponível para o estado atual.

```python
from sme_workflow_sdk import ContextoExecucao

# Validar a ação solicitada.
execucao = workflow.validar(
    estado_atual="pendente",
    acao="aprovar",
)

# A aplicação consumidora executa aqui suas regras de negócio.
# Exemplo: verificar as condições necessárias para aprovação.

# Criar o contexto da execução.
contexto = ContextoExecucao(
    autor="usuario_sistema",
    dados={
        "origem": "aplicacao_consumidora",
    },
)

# Gerar o resultado da transição.
resultado = workflow.executar(execucao, contexto)

if resultado["sucesso"]:
    novo_estado = resultado["proximo_estado"]

    # A aplicação consumidora é responsável por persistir
    # o novo estado e o histórico do processo.
```

**Importante:** o SDK não executa regras de negócio específicas nem realiza operações de persistência. A aplicação consumidora deve atualizar o estado somente após a conclusão bem-sucedida das regras de negócio, respeitando suas próprias regras transacionais.

## Resultado da execução

O método `MotorWorkflow.executar()` retorna um dicionário com informações sobre a transição realizada.

Entre os principais campos estão:

| Campo | Descrição |
|---|---|
| `sucesso` | Indica se a execução foi bem-sucedida. |
| `estado_anterior` | Estado em que a ação foi solicitada. |
| `acao` | Ação executada. |
| `proximo_estado` | Estado de destino da transição. |
| `terminal` | Indica se a transição é terminal. |
| `identificador` | Identificador da execução. |

A aplicação consumidora pode utilizar essas informações para atualizar o estado da entidade e registrar o histórico do processo.

Os campos `inicio` e `fim` são retornados como objetos `datetime`. Caso o resultado precise ser serializado em JSON, a aplicação deve realizar a conversão desses valores.

## Tratamento de exceções

O SDK disponibiliza exceções específicas para identificar falhas na leitura e validação da configuração e nas operações do workflow.

A aplicação consumidora deve tratar essas exceções conforme sua política de tratamento de erros, evitando considerar uma operação concluída quando ocorrer uma falha durante o processamento.

## Desenvolvimento

### Preparação do ambiente

Clone o repositório:

```bash
git clone https://github.com/prefeiturasp/SME-Workflow-SDK.git
cd SME-Workflow-SDK
```

Crie e ative um ambiente virtual:

```bash
python -m venv .venv
```

Linux/macOS:

```bash
source .venv/bin/activate
```

Windows (PowerShell):

```powershell
.venv\Scripts\Activate.ps1
```

Instale o projeto com as dependências de desenvolvimento e documentação:

```bash
python -m pip install -e ".[dev,docs]"
```

Instale os hooks de pre-commit:

```bash
pre-commit install
```

### Executar os testes

```bash
pytest
```

### Verificar a qualidade do código

```bash
ruff check .
mypy src/
pre-commit run --all-files
```

## Documentação

A documentação técnica do projeto é desenvolvida com **Sphinx** e está organizada no diretório `docs/`. Ela reúne os guias de utilização, configuração, integração e arquitetura do SDK, além da referência da API.

Os principais documentos são:

- [Primeiros passos](docs/primeiros_passos.md)
- [Configuração do workflow](docs/configurando_workflow.md)
- [Integração com a aplicação](docs/integrando_aplicacao.md)
- [Tratamento de exceções](docs/tratamento_excecoes.md)
- [Arquitetura](docs/arquitetura.md)
- [Referência da API](docs/api/index.rst)

A documentação também está disponível online, permitindo consultar os guias e a referência da API.
Para consultar a documentação publicada, acesse **[Documentação do SME-Workflow-SDK](https://prefeiturasp.github.io/SME-Workflow-SDK/)**


### Gerar a documentação localmente

Para limpar os arquivos gerados anteriormente e iniciar a documentação em modo de visualização automática, execute os comandos abaixo, na ordem apresentada:

```bash
# Limpa os arquivos de build anteriores
make -C docs clean

# Inicia a documentação com atualização automática
make -C docs livehtml
```

O comando `livehtml` inicia um servidor local para visualizar a documentação no navegador, atualizando a página conforme os arquivos são modificados.

Para gerar apenas a versão HTML estática, execute:

```bash
make -C docs html
```

Os arquivos HTML serão gerados no diretório `docs/_build/html/`.

## Licença

GNU Affero General Public License v3.0 (AGPL-3.0). Texto completo em
[`LICENSE`](LICENSE).
