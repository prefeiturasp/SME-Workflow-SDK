# Tratamento de exceções

O SME Workflow SDK utiliza exceções específicas para indicar problemas relacionados à configuração do workflow e à execução de suas operações.

O tratamento adequado dessas exceções permite que a aplicação consumidora identifique a causa da falha e apresente uma resposta apropriada, sem expor detalhes internos do SDK.

## 1. Categorias de exceções

As exceções do SDK estão organizadas em módulos de acordo com o contexto em que podem ocorrer.

### Exceções de configuração

Estão relacionadas à leitura e à validação do arquivo YAML utilizado para definir o workflow.

Podem ocorrer, por exemplo, quando:

- O arquivo de configuração não pode ser localizado ou lido.
- O conteúdo YAML possui formato inválido.
- A estrutura da configuração não atende ao contrato esperado.
- Existem estados ou transições inconsistentes.

Consulte o módulo `sme_workflow_sdk.excecoes.configuracao` para conhecer as exceções específicas dessa categoria.

### Exceções de workflow

Estão relacionadas à validação das operações do workflow.

Podem ocorrer quando:

- O estado informado não existe na configuração.
- A ação solicitada não está disponível para o estado atual.
- A transição configurada apresenta inconsistências.

Entre as exceções utilizadas nesse contexto estão:

| Exceção | Situação |
|---|---|
| `EstadoInvalidoError` | O estado informado não é válido no workflow. |
| `AcaoInvalidaError` | A ação solicitada não está disponível para o estado atual. |
| `TransicaoInvalidaError` | A transição configurada não atende às regras de consistência do workflow. |

Consulte o módulo `sme_workflow_sdk.excecoes.workflow` para conhecer a implementação dessas exceções.

## 2. Tratando exceções na validação

A aplicação consumidora deve tratar as exceções que podem ser lançadas durante a validação da ação.

```python
from sme_workflow_sdk import get_workflow
from sme_workflow_sdk.excecoes.workflow import (
    AcaoInvalidaError,
    EstadoInvalidoError,
    TransicaoInvalidaError,
)


def validar_acao(estado_atual, acao):
    motor = get_workflow()

    try:
        return motor.validar(
            estado_atual=estado_atual,
            acao=acao,
        )

    except EstadoInvalidoError:
        # Tratar estado não reconhecido.
        raise

    except AcaoInvalidaError:
        # Tratar ação não disponível para o estado.
        raise

    except TransicaoInvalidaError:
        # Tratar inconsistência na transição.
        raise
```

Os tratamentos apresentados são ilustrativos. A aplicação deve definir como cada situação será convertida em uma resposta adequada ao seu contexto.

## 3. Tratando falhas na inicialização

A inicialização do SDK pode falhar quando o arquivo YAML não puder ser carregado ou quando sua configuração não for válida.

Por isso, é importante tratar as exceções durante a inicialização da aplicação.

```python
from sme_workflow_sdk import configure


def inicializar_workflow():
    try:
        configure("workflow.yaml")

    except Exception:
        # Registrar a falha e impedir que a aplicação
        # utilize um workflow que não foi inicializado.
        raise
```

O exemplo utiliza `Exception` apenas para ilustrar o tratamento geral de uma falha de inicialização. Na aplicação, prefira capturar as exceções específicas de configuração disponibilizadas pelo SDK, conforme a necessidade.

## 4. Runtime não inicializado

As funções `get_workflow()` e operações que dependem do runtime exigem que o SDK tenha sido inicializado previamente.

Caso a aplicação tente recuperar o motor antes da inicialização, será lançada uma exceção `RuntimeError`.

```python
from sme_workflow_sdk import get_workflow


try:
    motor = get_workflow()

except RuntimeError:
    # O runtime ainda não foi inicializado.
    raise
```

Garanta que `configure()` seja executado antes de disponibilizar operações que dependam do workflow.

## 5. Boas práticas

Ao integrar o tratamento de exceções do SDK à aplicação, considere as seguintes recomendações:

- Inicialize o SDK antes de executar operações de workflow.
- Trate as exceções específicas sempre que precisar diferenciar os motivos da falha.
- Evite capturar exceções genéricas sem registrar ou tratar adequadamente o erro.
- Não exponha mensagens técnicas internas diretamente ao usuário final.
- Registre informações suficientes para permitir a investigação de falhas.
- Não atualize o estado persistido da entidade quando a validação ou as regras de negócio falharem.
- Mantenha as regras de tratamento e apresentação de erros sob responsabilidade da aplicação consumidora.

## 6. Referência da API

Para consultar a hierarquia e a implementação das exceções disponibilizadas pelo SDK, acesse a [Referência da API — Exceções](api/excecoes.rst).

Consulte também:

- [Primeiros passos](primeiros_passos.md)
- [Configurando o workflow](configurando_workflow.md)
- [Integrando com a aplicação](integrando_aplicacao.md)
