# Primeiros passos

Este guia apresenta o processo inicial para instalar o SME Workflow SDK, configurar um workflow e realizar a primeira integração em uma aplicação Python.

## Instalação

### Pré-requisitos

- Python 3.12 ou superior.
- Git.
- Acesso ao repositório do projeto.

### Instalar o SDK

Instale o SDK diretamente do repositório:

```bash
pip install git+https://github.com/prefeiturasp/SME-Workflow-SDK.git
```

Para instalar uma branch específica:

```bash
pip install git+https://github.com/prefeiturasp/SME-Workflow-SDK.git@NOME_DA_BRANCH
```

Substitua `NOME_DA_BRANCH` pelo nome da branch desejada.

## Criar o arquivo de workflow

O SDK utiliza arquivos YAML para declarar os estados, as ações disponíveis e as transições permitidas.

Crie um arquivo chamado `workflow.yaml`:

```yaml
estados:
  rascunho:
    acoes:
      enviar_para_analise:
        proximo_estado: aguardando_analise
        terminal: false

  aguardando_analise:
    acoes:
      aprovar:
        proximo_estado: aprovado
        terminal: true

      reprovar:
        proximo_estado: reprovado
        terminal: true

      solicitar_ajustes:
        proximo_estado: em_ajuste
        terminal: false

  em_ajuste:
    acoes:
      reenviar_para_analise:
        proximo_estado: aguardando_analise
        terminal: false

  aprovado:
    acoes: null

  reprovado:
    acoes: null
```

### Entendendo o workflow

O exemplo representa o fluxo de uma solicitação que precisa passar por análise antes de receber uma decisão.

Os estados representam as etapas do processo:

- **rascunho:** solicitação ainda não enviada para análise.
- **aguardando_analise:** solicitação disponível para análise.
- **em_ajuste:** solicitação devolvida para correções.
- **aprovado:** solicitação aprovada, encerrando o workflow.
- **reprovado:** solicitação reprovada, encerrando o workflow.

As ações definem as transições permitidas:

| Estado atual | Ação | Próximo estado | Terminal |
|---|---|---|---|
| `rascunho` | `enviar_para_analise` | `aguardando_analise` | Não |
| `aguardando_analise` | `aprovar` | `aprovado` | Sim |
| `aguardando_analise` | `reprovar` | `reprovado` | Sim |
| `aguardando_analise` | `solicitar_ajustes` | `em_ajuste` | Não |
| `em_ajuste` | `reenviar_para_analise` | `aguardando_analise` | Não |

### Estrutura da configuração

| Campo | Descrição |
|---|---|
| `estados` | Define os estados disponíveis no workflow. |
| `acoes` | Define as ações permitidas para cada estado. |
| `proximo_estado` | Identifica o estado de destino da ação. |
| `terminal` | Indica se a transição conduz a um estado terminal. |

O campo `terminal` deve receber um valor booleano (`true` ou `false`).

Um estado terminal deve possuir `acoes: null`, indicando que não existem novas ações disponíveis.

## Inicializar o SDK

O SDK disponibiliza um runtime para gerenciar a inicialização e o acesso à instância compartilhada do motor de workflow.

```python
from sme_workflow_sdk import configure, get_workflow

configure("workflow.yaml")

motor = get_workflow()
```

A função `configure()` carrega e valida a configuração YAML antes de inicializar o motor.

A inicialização é idempotente para o mesmo caminho de configuração. Caso o runtime já esteja inicializado com outro caminho, uma exceção será lançada.

## Validar uma ação

Com o motor inicializado, a aplicação pode verificar se uma ação está disponível para o estado atual.

Por exemplo, para enviar uma solicitação que está em rascunho para análise:

```python
execucao = motor.validar(
    estado_atual="rascunho",
    acao="enviar_para_analise",
)
```

O método `validar()` verifica:

- Se o estado informado existe na configuração.
- Se a ação está disponível para o estado atual.
- Se a transição configurada respeita as regras de consistência do workflow.

Se a validação for bem-sucedida, o método retorna uma instância de `ExecucaoValidada`, que contém os dados necessários para produzir o resultado da transição.

## Produzir o resultado da execução

Após validar a ação, a aplicação consumidora deve executar sua própria regra de negócio.

Quando a regra de negócio for concluída com sucesso, o resultado da transição pode ser produzido pelo SDK:

```python
from sme_workflow_sdk import ContextoExecucao

contexto = ContextoExecucao(
    autor="usuario_sistema",
    dados={
        "origem": "aplicacao_consumidora",
    },
)

resultado = motor.executar(execucao, contexto)

if resultado["sucesso"]:
    novo_estado = resultado["proximo_estado"]
```

O método `executar()` recebe os dados da transição previamente validados e o contexto da execução.

O resultado é um dicionário Python com informações como:

- Estado anterior.
- Ação executada.
- Próximo estado.
- Indicador de terminalidade.
- Indicador de sucesso.
- Identificador da execução.
- Autor e contexto.
- Horários de início e término.

**Importante:** o SDK não executa regras de negócio específicas da aplicação, não altera o estado persistido da entidade e não realiza operações de persistência.

A aplicação consumidora é responsável por persistir o novo estado e o histórico do processo após a conclusão bem-sucedida da operação.

## Encerrar o runtime

Quando necessário, a aplicação pode encerrar o runtime:

```python
from sme_workflow_sdk import shutdown

shutdown()
```

Após o encerramento, uma nova chamada a `get_workflow()` lançará `RuntimeError` até que o runtime seja inicializado novamente.

## Próximos passos

- [Configuração de workflows](configurando_workflow)
- [Integração com a aplicação](integrando_aplicacao)
- [Tratamento de exceções](tratamento_excecoes)
- [Referência da API](api/index)
