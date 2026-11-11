# Integração com a aplicação

Este guia apresenta como integrar o SME Workflow SDK a uma aplicação consumidora, utilizando o runtime e o motor de workflow para validar ações e produzir os resultados das transições.

O SDK é responsável por validar as transições configuradas e gerar o resultado da execução. As regras de negócio específicas, a atualização do estado da entidade e a persistência dos dados continuam sob responsabilidade da aplicação consumidora.

## 1. Inicialização do SDK

A inicialização deve ocorrer durante a inicialização da aplicação, antes de qualquer operação que utilize o workflow.

Utilize a função `configure()` para carregar e validar o arquivo YAML e inicializar o motor de workflow.

```python
from sme_workflow_sdk import configure

configure("workflow.yaml")
```

A inicialização é idempotente para o mesmo caminho de configuração. Caso o runtime já esteja inicializado com outro arquivo, será lançada uma exceção.

## 2. Obtendo o motor de workflow

Após a inicialização, utilize `get_workflow()` para obter a instância configurada do motor.

```python
from sme_workflow_sdk import get_workflow

motor = get_workflow()
```

Caso o runtime ainda não tenha sido inicializado, a chamada lançará uma exceção `RuntimeError`.

## 3. Validando uma ação

Antes de executar as regras de negócio associadas à operação, a aplicação deve validar se a ação solicitada está disponível para o estado atual da entidade.

Para isso, utilize o método `validar()`.

```python
execucao = motor.validar(
    estado_atual="aguardando_analise",
    acao="aprovar",
)
```

O método verifica:

- Se o estado informado está definido no workflow.
- Se a ação está disponível para o estado atual.
- Se a transição configurada respeita as regras de consistência do workflow.

Em caso de sucesso, retorna uma instância de `ExecucaoValidada`, contendo o estado atual, a ação validada e o horário de início da transição.

Se houver inconsistências, poderão ser lançadas exceções específicas, como `EstadoInvalidoError`, `AcaoInvalidaError` e `TransicaoInvalidaError`.

## 4. Executando as regras de negócio

Após a validação da ação, a aplicação consumidora deve executar suas próprias regras de negócio.

Por exemplo, ao aprovar uma solicitação, a aplicação pode precisar verificar informações adicionais, registrar a aprovação e atualizar outros dados relacionados.

Essas operações não são executadas pelo SDK.

```python
def aprovar_solicitacao(solicitacao):
    # Regras de negócio da aplicação.
    # Exemplo: verificar condições para aprovação.
    # Registrar informações da aprovação.
    pass
```

A aplicação deve garantir que as regras de negócio sejam executadas com sucesso antes de chamar `motor.executar()`.

## 5. Criando o contexto da execução

O `ContextoExecucao` reúne informações complementares da operação, como o autor responsável e dados adicionais fornecidos pela aplicação.

```python
from sme_workflow_sdk import ContextoExecucao

contexto = ContextoExecucao(
    autor="usuario_sistema",
    dados={
        "origem": "portal",
        "entidade": "solicitacao",
        "id_solicitacao": 123,
    },
)
```

O atributo `identificador` é gerado automaticamente quando não informado. A aplicação também pode fornecer seu próprio identificador.

O atributo `dados` recebe um mapeamento com informações adicionais e é protegido contra alterações diretas no mapeamento armazenado.

## 6. Gerando o resultado da transição

Depois que as regras de negócio forem executadas com sucesso, utilize `motor.executar()` para produzir o resultado da transição.

```python
resultado = motor.executar(
    dados_transicao=execucao,
    contexto=contexto,
)
```

O método retorna um dicionário com informações da execução, incluindo:

- Identificador da execução.
- Estado anterior.
- Ação executada.
- Próximo estado.
- Indicador de terminalidade.
- Indicador de sucesso.
- Mensagem do resultado.
- Data e hora de início e término.
- Autor responsável.
- Contexto associado.

Os valores de data e hora permanecem como objetos `datetime`, não sendo convertidos automaticamente para strings.

## 7. Atualizando o estado da entidade

O SDK não altera o estado persistido da entidade e não realiza operações de banco de dados.

A aplicação consumidora deve utilizar o resultado retornado para atualizar o estado da entidade e realizar a persistência conforme suas próprias regras.

```python
if resultado["sucesso"]:
    solicitacao.situacao = resultado["proximo_estado"]
    solicitacao.save()
```

A aplicação também é responsável por decidir como tratar falhas de negócio e garantir a consistência das operações de persistência.

## 8. Exemplo completo de integração

O exemplo abaixo reúne as etapas de validação, execução das regras de negócio, criação do contexto e geração do resultado.

```python
from sme_workflow_sdk import (
    ContextoExecucao,
    get_workflow,
)


def aprovar_solicitacao(solicitacao, usuario):
    motor = get_workflow()

    # 1. Validar a ação no estado atual.
    execucao = motor.validar(
        estado_atual=solicitacao.situacao,
        acao="aprovar",
    )

    # 2. Executar as regras de negócio da aplicação.
    # A operação deve ser concluída com sucesso antes
    # da geração do resultado do workflow.
    registrar_aprovacao(solicitacao, usuario)

    # 3. Criar o contexto da execução.
    contexto = ContextoExecucao(
        autor=str(usuario.id),
        dados={
            "id_solicitacao": solicitacao.id,
        },
    )

    # 4. Gerar o resultado da transição.
    resultado = motor.executar(
        dados_transicao=execucao,
        contexto=contexto,
    )

    # 5. Atualizar o estado da entidade na aplicação.
    if resultado["sucesso"]:
        solicitacao.situacao = resultado["proximo_estado"]
        solicitacao.save()

    return resultado
```

No exemplo, `registrar_aprovacao()` representa uma operação de negócio pertencente à aplicação consumidora. Ela não faz parte do SDK.

## 9. Encerrando o runtime

Quando necessário, utilize `shutdown()` para encerrar o runtime e remover a referência global ao motor.

```python
from sme_workflow_sdk import shutdown

shutdown()
```

Após o encerramento, chamadas a `get_workflow()` lançarão `RuntimeError` até que o runtime seja inicializado novamente.

Referências ao motor que tenham sido armazenadas externamente não são invalidadas automaticamente.

## 10. Responsabilidades da integração

A integração deve respeitar a separação de responsabilidades entre o SDK e a aplicação consumidora.

| Responsabilidade | Responsável |
|---|---|
| Carregar e validar a configuração YAML | SDK |
| Verificar se a ação é permitida no estado atual | SDK |
| Validar a consistência da transição | SDK |
| Executar regras de negócio específicas | Aplicação consumidora |
| Criar o contexto da execução | Aplicação consumidora |
| Produzir o resultado da transição | SDK |
| Atualizar o estado da entidade | Aplicação consumidora |
| Persistir as alterações | Aplicação consumidora |

Para conhecer os detalhes das classes e métodos utilizados neste guia, consulte a [Referência da API](api/index.md).

Consulte também [Configurando o workflow](configurando_workflow.md) e [Tratamento de exceções](tratamento_excecoes.md).
