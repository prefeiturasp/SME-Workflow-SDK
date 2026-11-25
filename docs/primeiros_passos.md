# Primeiros passos

Este guia apresenta a instalação do SME Workflow SDK, a configuração de um workflow e a primeira integração utilizando decorators.

## Instalação

### Pré-requisitos

- Python 3.12 ou superior.
- Git.
- Acesso ao repositório do projeto.

### Instalar o SDK

Atualmente, a instalação do SDK deve ser realizada informando explicitamente a branch `homolog`, que é a branch padrão disponibilizada para instalação.

Execute o comando:

```bash
pip install git+https://github.com/prefeiturasp/SME-Workflow-SDK.git@homolog
```

Caso seja necessário instalar uma versão de outra branch, substitua `homolog` pelo nome da branch desejada:

```bash
pip install git+https://github.com/prefeiturasp/SME-Workflow-SDK.git@NOME_DA_BRANCH
```

```{note}
Futuramente, a instalação poderá ser realizada sem informar a branch, utilizando diretamente o repositório.
```

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


## Declarar uma ação com decorator

O decorator `@workflow` associa um método da aplicação consumidora a um estado e uma ação definidos no YAML.

```python
from sme_workflow_sdk import processar_transicao
from sme_workflow_sdk.integracao import workflow


class SolicitacaoService:
    @workflow(estado="aguardando_analise", acao="aprovar")
    def aprovar(self, *, solicitacao, usuario):
        # Executar as regras de negócio da aplicação.
        # ...

        return processar_transicao(
            estado=solicitacao.status,
            acao="aprovar",
            autor=str(usuario.id),
        )
```

O decorator registra a associação quando o módulo é importado. Na chamada do método, o argumento nomeado `estado` é obrigatório e deve corresponder ao estado declarado. Esse argumento é consumido pelo decorator e não é repassado ao método original.

O decorator não executa automaticamente a transição. A aplicação chama `processar_transicao()` explicitamente dentro do método, no momento adequado às suas regras de negócio.


## Inicializar o SDK

A aplicação consumidora precisa apenas informar o caminho do arquivo YAML:

```python
from sme_workflow_sdk import configure

configure("workflow.yaml")
```

Durante a inicialização, o SDK carrega e valida a configuração YAML e disponibiliza o motor. Não verifica nesse momento se os estados e as ações declarados nos decorators estão presentes no YAML. Também não exige importações manuais dos serviços que utilizam `@workflow`.

## Executar uma ação

Após inicializar o SDK, utilize o serviço da aplicação:

```python
servico = SolicitacaoService()

resultado = servico.aprovar(
    estado=solicitacao.status,
    solicitacao=solicitacao,
    usuario=usuario,
)
```

O método executa as regras de negócio da aplicação e chama `processar_transicao()`, que valida a ação e retorna o resultado.

A função recebe o estado atual, a ação e o autor:

```python
resultado = processar_transicao(
    estado="aguardando_analise",
    acao="aprovar",
    autor="usuario_sistema",
)
```

O retorno é um dicionário. A aplicação pode utilizar `proximo_estado` para atualizar sua entidade:

```python
if resultado["sucesso"]:
    solicitacao.status = resultado["proximo_estado"]
    solicitacao.save()
```
```{important}
A persistência e o histórico permanecem sob responsabilidade da aplicação consumidora.
```
## Encerrar o runtime

Quando necessário:

```python
from sme_workflow_sdk import shutdown

shutdown()
```

## Próximos passos

- [Configurando o workflow](configurando_workflow.md)
- [Integrando com a aplicação](integrando_aplicacao.md)
- [Tratamento de exceções](tratamento_excecoes.md)
- [Referência da API](api/index.rst)
