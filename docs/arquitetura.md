# Arquitetura

## 1. Visão geral

O SME Workflow SDK é uma biblioteca Python reutilizável, projetada para centralizar o controle de estados e transições de processos de negócio por meio de configurações declarativas em YAML.

Seu principal objetivo é desacoplar as regras de fluxo operacional do código das aplicações consumidoras, permitindo que diferentes sistemas utilizem uma estrutura padronizada para validar ações e resolver transições.

A arquitetura foi concebida para ser independente de domínio, framework e banco de dados, possibilitando sua utilização em aplicações monolíticas, microsserviços e APIs REST.

O SDK é responsável por interpretar a configuração do workflow, validar as transições solicitadas e retornar o resultado da operação. A aplicação consumidora permanece responsável pelas regras de negócio, pela persistência e pelos efeitos decorrentes da transição.

## 2. Princípios arquiteturais

A arquitetura do SDK considera os seguintes princípios:

- **Separação de responsabilidades:** o SDK controla o fluxo, enquanto a aplicação consumidora mantém suas regras de negócio.
- **Baixo acoplamento:** o motor não depende de modelos, entidades ou estruturas específicas de uma aplicação.
- **Configuração declarativa:** estados e transições são definidos externamente em arquivos YAML.
- **Reutilização:** uma mesma implementação pode atender diferentes sistemas e domínios.
- **Testabilidade:** as regras de transição podem ser validadas independentemente da aplicação consumidora.
- **Independência de framework:** o SDK não exige o uso de um framework específico, como Django ou Flask.
- **Registro declarativo de ações:** a aplicação pode associar métodos a estados e ações por meio do decorator `@workflow`, sem transferir ao SDK a responsabilidade de executar regras de negócio.
- **Validação no momento adequado:** a configuração YAML é validada na inicialização, enquanto a validade de cada transição é verificada durante sua execução.

## 3. Estrutura de diretórios

O pacote `sme_workflow_sdk` está organizado em módulos que separam as responsabilidades de configuração, aplicação, domínio, integração, exceções e gerenciamento do runtime.

```text
sme_workflow_sdk/
│
├── __init__.py
├── py.typed
├── runtime.py
│
├── aplicacao/
│   ├── __init__.py
│   ├── motor_workflow.py
│   ├── decisao_resolver.py
│   └── transicao_resolver.py
│
├── configuracao/
│   ├── __init__.py
│   ├── configurador.py
│   ├── leitor.py
│   └── validador.py
│
├── dominio/
│   ├── __init__.py
│   ├── contexto.py
│   ├── entidades.py
│   ├── execucao_validada.py
│   ├── resultado.py
│   └── validacao.py
│
├── integracao/
│   ├── __init__.py
│   ├── decorators.py
│   └── registro_acoes.py
│
└── excecoes/
    ├── __init__.py
    ├── base.py
    ├── configuracao.py
    ├── workflow.py
    └── integracao.py
```

### 3.1 Organização dos módulos

| Diretório/arquivo | Responsabilidade |
|---|---|
| `__init__.py` | Disponibilizar os principais componentes e funções públicas do SDK. |
| `py.typed` | Indicar que o pacote disponibiliza informações de tipagem para ferramentas de análise estática. |
| `runtime.py` | Gerenciar a inicialização, recuperação, utilização e encerramento do runtime do workflow. |
| `aplicacao/` | Concentrar o motor e os componentes responsáveis pela validação e resolução das transições. |
| `configuracao/` | Realizar a leitura, configuração e validação dos arquivos YAML. |
| `dominio/` | Reunir as estruturas, o contexto, os resultados e os elementos de domínio utilizados pelo SDK. |
| `integracao/` | Disponibilizar o decorator `@workflow` e o registro centralizado das ações declaradas pela aplicação. |
| `excecoes/` | Organizar as exceções específicas do SDK, incluindo erros de configuração, workflow e integração. |

Essa organização mantém as responsabilidades separadas e facilita a manutenção, a evolução e a reutilização do SDK.

### 3.2 Módulo de integração

O pacote `integracao` concentra os mecanismos que permitem à aplicação consumidora declarar métodos associados aos estados e às ações do workflow.

Seus componentes são:

| Arquivo | Responsabilidade |
|---|---|
| `decorators.py` | Disponibilizar o decorator `@workflow`, utilizado para declarar o estado e a ação associados a um método. |
| `registro_acoes.py` | Manter o registro centralizado das associações entre estado, ação e método declarado. |

O registro é realizado quando o módulo que contém o método decorado é importado pelo Python. Portanto, a aplicação consumidora deve garantir que os módulos que declaram ações sejam importados antes de chamar esses métodos.

O registro dos decorators é independente do ciclo de inicialização do runtime. O SDK não realiza descoberta automática de módulos da aplicação e não exige que os métodos registrados sejam validados contra o YAML durante `configure()`.

## 4. Componentes arquiteturais

A estrutura do SDK está organizada em módulos que separam configuração, aplicação, domínio, integração, exceções e gerenciamento do runtime.

### 4.1 Runtime

O módulo `runtime` gerencia o ciclo de vida da instância compartilhada do motor de workflow e oferece o ponto de entrada para as aplicações consumidoras.

Suas principais responsabilidades são:

- Inicializar o SDK a partir de um arquivo YAML.
- Disponibilizar a instância configurada do motor.
- Encaminhar solicitações de processamento de transições.
- Encerrar o runtime quando necessário.

As principais funções disponibilizadas são:

| Função | Responsabilidade |
|---|---|
| `configure()` | Carregar e validar a configuração YAML e inicializar o motor. |
| `get_workflow()` | Recuperar a instância configurada do motor. |
| `processar_transicao()` | Encaminhar ao motor a solicitação de transição e retornar o resultado em formato de dicionário. |
| `shutdown()` | Encerrar o runtime e liberar a instância compartilhada. |

A inicialização é realizada informando o caminho do arquivo YAML:

```python
from sme_workflow_sdk import configure

configure("workflow.yaml")
```

Durante esse processo, o SDK carrega o arquivo e valida sua estrutura e consistência. A instância do motor somente fica disponível após a conclusão dessas etapas.

A inicialização **não valida as declarações realizadas com `@workflow`**. Também não exige que a aplicação informe diretórios, pacotes ou módulos para descoberta de métodos decorados.

### 4.2 Configuração

O pacote `configuracao` é responsável por carregar e validar a configuração declarativa do workflow.

É composto pelos seguintes componentes:

| Classe | Responsabilidade |
|---|---|
| `LeitorWorkflow` | Realizar a leitura do arquivo YAML. |
| `ValidadorWorkflow` | Verificar a estrutura e a consistência da configuração. |
| `ConfiguradorWorkflow` | Coordenar o carregamento e a validação da configuração. |

A configuração define os estados disponíveis, as ações permitidas e os respectivos destinos ou decisões associados às transições.

A validação realizada durante a inicialização verifica o próprio documento YAML. Ela não percorre o registro de decorators nem verifica se todas as declarações feitas pela aplicação estão presentes no arquivo.

### 4.3 Aplicação

O pacote `aplicacao` concentra a lógica de execução do motor de workflow.

Seus componentes são:

| Classe | Responsabilidade |
|---|---|
| `MotorWorkflow` | Coordenar a validação e o processamento das transições solicitadas. |
| `DecisaoResolver` | Resolver a decisão configurada para uma ação. |
| `TransicaoResolver` | Resolver as informações da transição entre estados. |

O motor utiliza a configuração carregada e validada para verificar cada solicitação de transição, identificar o próximo estado e determinar se o estado resultante é terminal.

A operação de processamento recebe o estado atual, a ação e o autor da operação. O resultado é retornado como um dicionário, permitindo que a aplicação consumidora utilize as informações sem precisar manipular diretamente as estruturas internas do motor.

Exemplo de utilização pela aplicação:

```python
from sme_workflow_sdk import processar_transicao

resultado = processar_transicao(
    estado="pendente",
    acao="aprovar",
    autor=str(usuario.id),
)

if resultado["sucesso"]:
    solicitacao.status = resultado["proximo_estado"]
    solicitacao.save()
```

O exemplo representa a utilização do resultado pela aplicação. A persistência da entidade continua sendo responsabilidade do sistema consumidor.

### 4.4 Domínio

O pacote `dominio` reúne as estruturas e regras fundamentais do workflow, sem depender de elementos específicos da aplicação consumidora.

Entre suas principais estruturas estão:

| Classe ou módulo | Responsabilidade |
|---|---|
| `ContextoExecucao` | Representar informações complementares utilizadas durante o processamento. |
| `ExecucaoValidada` | Representar os dados de uma transição após a validação necessária. |
| `ResultadoWorkflow` | Representar o resultado produzido pelo motor. |
| `validacao` | Reunir regras de validação utilizadas pelo domínio. |
| `entidades` | Reunir estruturas de domínio utilizadas pelo SDK. |

Essas estruturas permitem que o processamento seja realizado sem acoplamento a modelos ou entidades da aplicação consumidora.

### 4.5 Integração: decorator e registro de ações

O pacote `integracao` disponibiliza o decorator `@workflow` e o registro centralizado utilizado para associar métodos a estados e ações.

O decorator é declarado com os parâmetros `estado` e `acao`:

```python
from sme_workflow_sdk.integracao import workflow

class SolicitacaoService:

    @workflow(estado="pendente", acao="aprovar")
    def aprovar(self, *, solicitacao, usuario):
        # Regras de negócio da aplicação
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

O decorator possui as seguintes responsabilidades:

- Declarar o estado e a ação associados ao método.
- Registrar a associação no registro centralizado do SDK.
- Verificar, no momento da chamada do método, se o estado recebido corresponde ao estado declarado.
- Encaminhar a chamada ao método original quando a verificação do estado for satisfeita.

O argumento `estado` é recebido pelo wrapper do decorator para realizar essa verificação e não é repassado ao método original. Por isso, o método decorado não deve declarar `estado` em sua assinatura.

A chamada do método deve informar o estado por argumento nomeado:

```python
servico.aprovar(
    estado=solicitacao.status,
    solicitacao=solicitacao,
    usuario=usuario,
)
```

O decorator não executa as regras de negócio do método, não realiza a transição no motor e não substitui a validação de transição feita por `processar_transicao()`.

#### Registro das ações

O registro centralizado mantém as associações entre o par `(estado, acao)` e o método declarado.

A mesma ação pode ser registrada para estados diferentes. Entretanto, uma associação já registrada para o mesmo par `(estado, acao)` não deve ser sobrescrita por outro método.

O registro ocorre durante a importação do módulo que contém a declaração do decorator. Isso significa que o Python precisa importar o módulo para executar o decorator e efetuar o registro.

O registro não é utilizado para validar declarações durante a inicialização do runtime. Assim, a ausência de uma declaração no YAML não impede, por si só, que `configure()` inicialize o motor. A validade da transição solicitada será verificada pelo motor quando `processar_transicao()` for executado.

### 4.6 Exceções

O pacote `excecoes` organiza as exceções específicas do SDK, permitindo identificar falhas relacionadas à configuração, às operações do workflow e à integração.

A separação das exceções facilita o tratamento dos erros pelas aplicações consumidoras.

As exceções estão distribuídas em módulos conforme sua responsabilidade:

| Módulo | Responsabilidade |
|---|---|
| `base.py` | Definir a exceção-base do SDK. |
| `configuracao.py` | Agrupar exceções relacionadas à leitura e validação da configuração. |
| `workflow.py` | Agrupar exceções relacionadas aos estados, ações e processamento do workflow. |
| `integracao.py` | Agrupar exceções relacionadas à declaração e à integração dos métodos com o SDK. |

## 5. Fluxo arquitetural

Esta seção apresenta a comunicação entre a aplicação consumidora e os componentes internos do SDK, desde a inicialização até a utilização do resultado da transição.

### 5.1 Inicialização

```text
Aplicação consumidora
        |
        | configure("workflow.yaml")
        v
      Runtime
        |
        v
  ConfiguradorWorkflow
        |
        +------------------+
        |                  |
        v                  v
   LeitorWorkflow    ValidadorWorkflow
        |                  |
        +--------+---------+
                 |
                 v
           MotorWorkflow
                 |
                 v
       Runtime inicializado
```

O runtime coordena a inicialização. O configurador realiza a leitura e a validação do YAML e, após a conclusão dessas etapas, o motor é criado e disponibilizado.

A inicialização não percorre os módulos da aplicação, não importa serviços automaticamente e não valida as declarações realizadas com `@workflow`.

### 5.2 Declaração e registro dos métodos

```text
Aplicação consumidora
        |
        v
Importação do módulo
        |
        v
Método decorado com @workflow
        |
        v
Decorator
        |
        +-------------------------+
        |                         |
        v                         v
Declara estado e ação      Registro de ações
        |
        v
Método disponível
```

Quando a aplicação importa um módulo que contém um método decorado, o decorator é executado e registra a associação entre estado, ação e método.

Esse fluxo é independente da inicialização do runtime. O SDK não realiza a descoberta automática desses módulos.

### 5.3 Chamada do método decorado

```text
Aplicação consumidora
        |
        | Chamada com estado
        v
     Decorator
        |
        v
Verificação do estado informado
        |
        +--------------------------+
        |                          |
        v                          v
Estado compatível           Estado incompatível
        |                          |
        v                          v
Método original          Exceção de integração
```

Na chamada do método, o decorator compara o estado informado com o estado declarado. Se forem compatíveis, a execução é encaminhada ao método original. Caso contrário, é lançada a exceção correspondente.

Essa verificação não substitui a validação da transição pelo motor.

### 5.4 Validação e resolução da transição

```text
Aplicação consumidora
        |
        | Estado atual + ação + autor
        v
 processar_transicao()
        |
        v
   MotorWorkflow
        |
        v
 Validação da transição
        |
        v
  DecisaoResolver
        |
        v
 TransicaoResolver
        |
        v
 ResultadoWorkflow
        |
        v
Aplicação consumidora
```

A aplicação informa o estado atual, a ação solicitada e o autor. O motor verifica se o estado e a ação são válidos conforme o YAML, resolve a transição configurada e retorna o resultado para a aplicação consumidora.

A validação é realizada no momento da execução da transição, não durante a inicialização do runtime.

### 5.5 Operações da aplicação consumidora

```text
      Aplicação consumidora
                |
                v
        Regras de negócio
                |
         +------+------+
         |             |
         v             v
    Persistência   Auditoria e
                   notificações
```

Após receber o resultado do SDK, a aplicação executa as operações de sua responsabilidade, incluindo atualização de estado, persistência e eventuais operações complementares.

Os diagramas representam uma visão conceitual da integração e não necessariamente a sequência exata de todas as chamadas internas do código.

## 6. Responsabilidades do SDK e da aplicação consumidora

A separação de responsabilidades é um dos principais objetivos arquiteturais do projeto.

| Responsabilidade | SDK | Aplicação consumidora |
|---|:---:|:---:|
| Carregar configuração YAML | Sim | Não |
| Validar estrutura e consistência do YAML | Sim | Não |
| Disponibilizar o motor de workflow | Sim | Não |
| Declarar associações entre métodos, estados e ações por decorator | Sim, por meio da integração | Utiliza o decorator |
| Registrar associações declaradas pelos decorators | Sim | Importa os módulos que contêm as declarações |
| Descobrir e importar automaticamente módulos da aplicação | Não | Sim, quando necessário |
| Validar o estado recebido na chamada do método decorado | Sim, pelo decorator | Informa o estado na chamada |
| Validar a transição solicitada conforme o YAML | Sim | Não |
| Resolver o próximo estado | Sim | Não |
| Produzir o resultado da transição | Sim | Não |
| Executar regras de negócio específicas | Não | Sim |
| Persistir alterações no banco de dados | Não | Sim |
| Registrar auditoria e histórico persistido | Não | Sim |
| Enviar notificações | Não | Sim |
| Executar integrações externas | Não | Sim |

O SDK não deve conhecer modelos de banco de dados, serviços, repositórios ou regras específicas dos sistemas que o utilizam.

A aplicação consumidora utiliza as informações produzidas pelo SDK para executar suas próprias operações, mantendo o controle sobre os efeitos de negócio e a persistência dos dados.

## 7. Limites arquiteturais

O SDK não tem como objetivo substituir uma plataforma corporativa de BPM ou uma engine completa de gerenciamento de processos.

Não fazem parte de suas responsabilidades atuais:

- Orquestração distribuída de processos.
- Modelagem de processos BPMN.
- Gerenciamento humano de tarefas.
- Agendamento de atividades.
- Mensageria nativa.
- Interface gráfica para desenho de workflows.
- Persistência de entidades da aplicação consumidora.
- Execução de regras de negócio específicas do domínio.
- Descoberta e importação automática de módulos da aplicação consumidora.

Essas funcionalidades podem ser implementadas pelas aplicações consumidoras ou por componentes externos, conforme as necessidades de cada sistema.

## 8. Referências

Para aprofundar o entendimento da implementação e da utilização do SDK, consulte:

- [Primeiros passos](primeiros_passos.md)
- [Configurando o workflow](configurando_workflow.md)
- [Integrando com a aplicação](integrando_aplicacao.md)
- [Tratamento de exceções](tratamento_excecoes.md)
- [Referência da API](api/index.rst)
