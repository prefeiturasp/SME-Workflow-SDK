# SME-Workflow-SDK

[![python](https://img.shields.io/badge/python-3.12-blue.svg)]()
[![license](https://img.shields.io/badge/license-AGPL--3.0-green.svg)]()

## Objetivo e escopo

O **SME-Workflow-SDK** é uma biblioteca Python para gerenciamento de workflows configuráveis. Utiliza arquivos YAML para declarar estados, ações e transições e oferece recursos para associar métodos da aplicação consumidora às ações do fluxo.

O SDK é independente do domínio de negócio e de frameworks específicos, podendo ser utilizado em aplicações Python, incluindo sistemas desenvolvidos com Django.

### Responsabilidades do SDK

- Carregar e validar configurações de workflow em YAML.
- Registrar as associações declaradas com `@workflow`.
- Verificar a compatibilidade entre o estado recebido na chamada de um método decorado e o estado declarado.
- Validar a ação solicitada e resolver a transição.
- Retornar o resultado estruturado do processamento.

### Responsabilidades da aplicação consumidora

- Implementar e executar as regras de negócio dos métodos decorados.
- Chamar `processar_transicao()` no momento adequado do fluxo da aplicação.
- Persistir o novo estado e o histórico do processo.
- Gerenciar permissões, auditoria, notificações e demais efeitos externos.

O decorator não executa automaticamente a transição no motor. Ele registra a associação e verifica a compatibilidade do estado informado na chamada. O processamento da transição é solicitado explicitamente pela aplicação por meio de `processar_transicao()`.

## Funcionalidades

- Configuração declarativa de workflows por YAML.
- Validação estrutural e semântica da configuração.
- Declaração de ações por meio do decorator `@workflow`.
- Registro centralizado das combinações de estado e ação.
- Validação do estado informado na chamada de métodos decorados.
- Prevenção de registros duplicados para a mesma combinação.
- Processamento de transições por uma interface pública.
- Resultado estruturado com informações da transição.
- Separação entre controle do workflow e regras de negócio.

## Instalação

### Pré-requisitos

- Python 3.12 ou superior.
- Git, para instalação diretamente do repositório.
- Acesso ao repositório do projeto.

Atualmente, a instalação do SDK deve ser realizada informando explicitamente a branch `homolog`, que é a branch padrão disponibilizada para instalação.

```bash
pip install git+https://github.com/prefeiturasp/SME-Workflow-SDK.git@homolog
```

Para instalar uma branch específica:

```bash
pip install git+https://github.com/prefeiturasp/SME-Workflow-SDK.git@NOME_DA_BRANCH
```

Substitua `NOME_DA_BRANCH` pelo nome da branch desejada.

> Futuramente, a instalação poderá ser realizada sem informar a branch, utilizando diretamente o repositório.

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

| Campo | Descrição |
|---|---|
| `estados` | Define os estados disponíveis no workflow. |
| `acoes` | Define as ações permitidas para um estado. |
| `proximo_estado` | Informa o estado de destino da ação. |
| `terminal` | Indica se a transição encerra o fluxo. |

O campo `terminal` deve receber um valor booleano (`true` ou `false`). Estados sem ações disponíveis devem ser declarados com `acoes: null`.

## Integração com a aplicação

### 1. Inicialize o SDK

A aplicação consumidora precisa apenas informar o caminho do arquivo YAML. Não é necessário importar previamente os serviços que utilizam `@workflow`, nem informar diretórios ou pacotes para descoberta de módulos.

```python
from sme_workflow_sdk import configure

configure("workflow.yaml")
```

Durante a inicialização, o SDK carrega e valida a estrutura e a consistência da configuração YAML e, em seguida, disponibiliza o motor. A inicialização não verifica se as declarações dos decorators correspondem ao YAML.

### 2. Declare os métodos associados às ações

Utilize `@workflow` para associar um método a uma combinação de estado e ação:

```python
from sme_workflow_sdk import processar_transicao
from sme_workflow_sdk.integracao import workflow


class SolicitacaoService:
    @workflow(estado="pendente", acao="aprovar")
    def aprovar(self, *, solicitacao, usuario):
        # Regras de negócio da aplicação consumidora.
        # ...

        return processar_transicao(
            estado=solicitacao.status,
            acao="aprovar",
            autor=str(usuario.id),
        )
```

O decorator exige que a chamada do método receba o argumento nomeado `estado`. Esse argumento é utilizado para verificar se o estado atual corresponde ao declarado e não é repassado ao método original.

Os demais argumentos são destinados à implementação do método e podem representar a entidade, o usuário ou outras informações necessárias às regras de negócio.

### 3. Chame o método e processe a transição

```python
servico = SolicitacaoService()

resultado = servico.aprovar(
    estado=solicitacao.status,
    solicitacao=solicitacao,
    usuario=usuario,
)
```

O método decorado executa as regras de negócio da aplicação e solicita explicitamente o processamento da transição por meio de `processar_transicao()`.

A função recebe:

- `estado`: estado atual do processo;
- `acao`: ação configurada para o estado;
- `autor`: identificação textual do responsável.

A função retorna um dicionário com o resultado da transição. Por exemplo:

```python
if resultado["sucesso"]:
    solicitacao.status = resultado["proximo_estado"]
    solicitacao.save()
```

A persistência continua sendo responsabilidade da aplicação consumidora.

## Comportamento do decorator e do registro

- Uma mesma ação pode ser declarada em estados diferentes.
- A mesma combinação de estado e ação não pode ser registrada por métodos diferentes.
- O registro da mesma função para a mesma combinação é idempotente.
- O estado recebido na chamada do método decorado deve ser igual ao estado declarado.
- A declaração do decorator é registrada quando o módulo que a contém é importado pelo fluxo normal da aplicação.
- O decorator verifica, na chamada do método, se o estado recebido corresponde ao estado declarado.
- A consistência da transição com o YAML é verificada quando `processar_transicao()` é executado.

## Resultado do processamento

`processar_transicao()` retorna um dicionário com informações da transição, incluindo:

| Campo | Descrição |
|---|---|
| `sucesso` | Indica se o processamento foi concluído. |
| `estado_anterior` | Estado em que a ação foi solicitada. |
| `acao` | Ação processada. |
| `proximo_estado` | Estado de destino da transição. |
| `terminal` | Indica se a transição é terminal. |
| `identificador` | Identificador gerado para a execução. |
| `autor` | Identificação do responsável. |
| `inicio` / `fim` | Datas e horários do processamento. |

Os campos de data e hora são objetos `datetime`; a aplicação deve convertê-los caso precise serializar o resultado em JSON.

## Ciclo de vida do runtime

Inicialize o SDK uma vez durante a inicialização da aplicação:

```python
from sme_workflow_sdk import configure

configure("workflow.yaml")
```

Quando necessário, encerre o runtime:

```python
from sme_workflow_sdk import shutdown

shutdown()
```

A inicialização é idempotente para o mesmo caminho de configuração. Uma tentativa de inicializar o runtime com outro caminho enquanto ele já estiver ativo gera `RuntimeError`.

## Tratamento de exceções

O SDK disponibiliza exceções específicas para falhas de configuração, declarações dos decorators e processamento de transições. A aplicação consumidora deve tratar essas exceções de acordo com seu contexto.

Entre os erros possíveis estão:

- Estado ou ação inexistente na configuração.
- Declaração duplicada para a mesma combinação de estado e ação.
- Estado recebido diferente do estado declarado no decorator.
- Runtime ainda não inicializado.
- Falhas na leitura ou validação do YAML.

Consulte [Tratamento de exceções](docs/tratamento_excecoes.md) para mais detalhes.

## Desenvolvimento

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

Execute os testes e verificações:

```bash
pytest
ruff check .
mypy src/
pre-commit run --all-files
```

## Documentação

A documentação técnica utiliza **Sphinx** e está organizada no diretório `docs/`.

- [Primeiros passos](docs/primeiros_passos.md)
- [Configuração do workflow](docs/configurando_workflow.md)
- [Integração com a aplicação](docs/integrando_aplicacao.md)
- [Tratamento de exceções](docs/tratamento_excecoes.md)
- [Arquitetura](docs/arquitetura.md)
- [Referência da API](docs/api/index.rst)

A documentação também está disponível online, permitindo consultar os guias e a referência da API.
Para consultar a documentação publicada, acesse **[Documentação do SME-Workflow-SDK](https://prefeiturasp.github.io/SME-Workflow-SDK/)**

Para gerar a documentação localmente:

```bash
make -C docs clean
make -C docs html
```

Os arquivos HTML serão gerados em `docs/_build/html/`. Para visualizar com atualização automática, utilize `make -C docs livehtml`.

## Licença

GNU Affero General Public License v3.0 (AGPL-3.0). Texto completo em [`LICENSE`](LICENSE).
