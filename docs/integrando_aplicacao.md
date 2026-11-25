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

Durante `configure()`, o SDK:

1. Carrega o arquivo YAML.
2. Valida a estrutura e a consistência da configuração.
3. Instancia e disponibiliza o motor.



A chamada de `configure()` com o mesmo caminho já utilizado é idempotente. Se o runtime estiver ativo com outro caminho, será lançada `RuntimeError`.


## 2. Declarando métodos com `@workflow`

Importe o decorator:

```python
from sme_workflow_sdk.integracao import workflow
```

Associe o método ao estado e à ação correspondentes no YAML:

```python
class SolicitacaoService:
    @workflow(estado="aguardando_analise", acao="aprovar")
    def aprovar(self, *, solicitacao, usuario):
        # Regras de negócio da aplicação consumidora.
        self.validar_aprovacao(solicitacao, usuario)

        resultado = processar_transicao(
            estado=solicitacao.status,
            acao="aprovar",
            autor=str(usuario.id),
        )

        if resultado["sucesso"]:
            solicitacao.status = resultado["proximo_estado"]
            solicitacao.save()

        return resultado
```

O decorator recebe somente `estado` e `acao` na declaração. Na chamada do método, o argumento nomeado `estado` é obrigatório.

O decorator compara o estado recebido com o estado declarado. Se forem diferentes, lança `EstadoWorkflowIncompativelError`. O argumento `estado` é consumido pelo wrapper e não é repassado ao método original; os demais argumentos são preservados.

O decorator não chama o motor nem processa a transição automaticamente. A implementação do método deve chamar `processar_transicao()` explicitamente, depois de executar as regras de negócio necessárias.

## 3. Registro das declarações

Quando um módulo contendo um método decorado é importado, a associação entre estado, ação e método é registrada no registro centralizado do SDK.

O registro:

- Permite a mesma ação em estados diferentes.
- Impede métodos diferentes para a mesma combinação de estado e ação.
- Trata o registro repetido da mesma função para a mesma combinação como idempotente.
- Armazena a função original, sem instanciar serviços da aplicação consumidora.

O registro do decorator acontece quando o Python importa o módulo que contém o método decorado. Entretanto, a inicialização do SDK não depende desse registro: não é necessário importar previamente os serviços para executar `configure()`. A aplicação importa e utiliza seus serviços normalmente, conforme sua própria organização.


## 4. Processando uma transição

A aplicação utiliza `processar_transicao()` para solicitar explicitamente o processamento:

```python
from sme_workflow_sdk import processar_transicao

resultado = processar_transicao(
    estado="aguardando_analise",
    acao="aprovar",
    autor=str(usuario.id),
)
```

A função encaminha os parâmetros para o motor configurado. O motor valida se o estado existe, se a ação está disponível e se a transição respeita as regras de consistência do workflow.

O retorno é um dicionário com informações da operação, incluindo:

- `identificador`: identificador da execução;
- `estado_anterior`: estado atual informado;
- `acao`: ação processada;
- `proximo_estado`: estado de destino;
- `terminal`: indicador de transição terminal;
- `sucesso`: indicador de sucesso;
- `autor`: identificação do responsável;
- `inicio` e `fim`: horários do processamento.

Os valores de `inicio` e `fim` são objetos `datetime`. A aplicação deve convertê-los quando precisar serializar o resultado.


## 5. Atualizando o estado da entidade

O SDK não altera o estado persistido da entidade e não realiza operações de banco de dados.

A aplicação consumidora deve utilizar o resultado retornado para atualizar o estado da entidade e realizar a persistência conforme suas próprias regras.

```python
if resultado["sucesso"]:
    solicitacao.situacao = resultado["proximo_estado"]
    solicitacao.save()
```

A aplicação também é responsável por decidir como tratar falhas de negócio e garantir a consistência das operações de persistência.

## 6. Exemplo completo de integração

O exemplo demonstra a declaração, a inicialização e a chamada de um método decorado:

```python
from sme_workflow_sdk import configure, processar_transicao
from sme_workflow_sdk.integracao import workflow


class SolicitacaoService:
    @workflow(estado="pendente", acao="aprovar")
    def aprovar(self, *, solicitacao, usuario):
        # Regras de negócio específicas da aplicação.
        self.validar_aprovacao(solicitacao, usuario)

        resultado = processar_transicao(
            estado=solicitacao.status,
            acao="aprovar",
            autor=str(usuario.id),
        )

        if resultado["sucesso"]:
            solicitacao.status = resultado["proximo_estado"]
            solicitacao.save()

        return resultado


# Inicialização independente dos módulos que declaram decorators.
configure("workflow.yaml")

servico = SolicitacaoService()
resultado = servico.aprovar(
    estado=solicitacao.status,
    solicitacao=solicitacao,
    usuario=usuario,
)
```

`validar_aprovacao()` representa uma regra de negócio da aplicação e não faz parte do SDK.

## 7. Encerrando o runtime

Quando necessário, utilize `shutdown()` para encerrar o runtime e remover a referência global ao motor.

```python
from sme_workflow_sdk import shutdown

shutdown()
```

Após o encerramento, chamadas a `processar_transicao()` falharão porque o runtime não estará inicializado. Uma nova chamada a `configure()` poderá inicializá-lo novamente.

## 8. Responsabilidades da integração

A integração deve respeitar a separação de responsabilidades entre o SDK e a aplicação consumidora.

| Responsabilidade | Responsável |
|---|---|
| Declarar associações entre métodos, estados e ações | Aplicação, por meio de `@workflow` |
| Registrar as declarações | SDK |
| Verificar estado informado na chamada do método decorado | SDK |
| Verificar compatibilidade do estado na chamada do método | Decorator do SDK |
| Executar regras de negócio | Aplicação consumidora |
| Solicitar o processamento da transição | Aplicação consumidora |
| Validar a ação e resolver a transição | SDK |
| Atualizar e persistir a entidade | Aplicação consumidora |
| Registrar histórico, auditoria e notificações | Aplicação consumidora |

Para conhecer os detalhes das classes e métodos utilizados neste guia, consulte a [Referência da API](api/index.rst).

Consulte também [Configurando o workflow](configurando_workflow.md) e [Tratamento de exceções](tratamento_excecoes.md).
