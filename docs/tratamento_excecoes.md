# Tratamento de exceções

O SME Workflow SDK utiliza exceções específicas para indicar problemas na configuração, nas declarações dos decorators, na inicialização do runtime e no processamento das transições.

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


## Exceções de integração

O pacote de integração disponibiliza exceções relacionadas às declarações realizadas pelos decorators.

| Exceção | Situação |
|---|---|
| `DeclaracaoWorkflowInvalidaError` | O estado ou a ação declarados são inválidos, ou o decorator foi aplicado a um objeto não chamável. |
| `AcaoDuplicadaError` | Outro método já está registrado para a mesma combinação de estado e ação. |
| `EstadoWorkflowIncompativelError` | O estado recebido na chamada do método decorado é diferente do estado declarado. |

Essas exceções podem ocorrer durante a execução de `processar_transicao()`, quando o estado ou a ação solicitados não forem compatíveis com a configuração YAML. A inicialização não compara as declarações dos decorators com o YAML.


## 2. Falhas no processamento

A aplicação solicita o processamento por meio de `processar_transicao()`:

```python
from sme_workflow_sdk import processar_transicao

resultado = processar_transicao(
    estado="aguardando_analise",
    acao="aprovar",
    autor="usuario_sistema",
)
```

A chamada pode lançar exceções quando o runtime não estiver inicializado, o estado não existir, a ação não estiver disponível ou a transição for inválida.

Exemplo de tratamento:

```python
from sme_workflow_sdk import processar_transicao
from sme_workflow_sdk.excecoes.workflow import (
    AcaoInvalidaError,
    EstadoInvalidoError,
    TransicaoInvalidaError,
)

try:
    resultado = processar_transicao(
        estado="aguardando_analise",
        acao="aprovar",
        autor="usuario_sistema",
    )
except EstadoInvalidoError:
    # Tratar estado não reconhecido.
    raise
except AcaoInvalidaError:
    # Tratar ação não permitida.
    raise
except TransicaoInvalidaError:
    # Tratar transição inconsistente.
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

`processar_transicao()` depende do runtime configurado. Se a aplicação tentar processar uma transição antes de chamar `configure()`, será lançada `RuntimeError`.

Garanta que o SDK seja inicializado antes de disponibilizar operações que dependam do workflow.

## 5. Boas práticas

- Garanta que os módulos que contêm serviços decorados sejam importados normalmente pela aplicação antes de utilizar esses serviços.
- Inicialize o SDK antes de processar transições.
- Trate exceções específicas quando precisar diferenciar as causas da falha.
- Registre informações suficientes para investigar erros.
- Não atualize o estado persistido quando o processamento ou as regras de negócio falharem.
- Mantenha o tratamento e a apresentação de erros sob responsabilidade da aplicação consumidora.

## 6. Referência da API

Para consultar a hierarquia e a implementação das exceções disponibilizadas pelo SDK, acesse a [Referência da API — Exceções](api/excecoes.rst).

Consulte também:

- [Primeiros passos](primeiros_passos.md)
- [Configurando o workflow](configurando_workflow.md)
- [Integrando com a aplicação](integrando_aplicacao.md)
