# Arquitetura

## 1. Visão geral

O SME Workflow SDK é uma biblioteca Python reutilizável, projetada para centralizar o controle de estados e transições de processos de negócio por meio de configurações declarativas em YAML.

Seu principal objetivo é desacoplar as regras de fluxo operacional do código das aplicações consumidoras, permitindo que diferentes sistemas utilizem uma estrutura padronizada para validar ações e resolver transições.

A arquitetura foi concebida para ser independente de domínio, framework e banco de dados, possibilitando sua utilização em aplicações monolíticas, microsserviços e APIs REST.

## 2. Princípios arquiteturais

A arquitetura do SDK considera os seguintes princípios:

- **Separação de responsabilidades:** o SDK controla o fluxo, enquanto a aplicação consumidora mantém suas regras de negócio.
- **Baixo acoplamento:** o motor não depende de modelos, entidades ou estruturas específicas de uma aplicação.
- **Configuração declarativa:** estados e transições são definidos externamente em arquivos YAML.
- **Reutilização:** uma mesma implementação pode atender diferentes sistemas e domínios.
- **Testabilidade:** as regras de transição podem ser validadas independentemente da aplicação consumidora.

## 3. Estrutura de diretórios

O pacote `sme_workflow_sdk` está organizado em módulos que separam as responsabilidades de configuração, aplicação, domínio, exceções e gerenciamento do runtime.

```text
sme_workflow_sdk/
│
├── __init__.py
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
└── excecoes/
    ├── __init__.py
    ├── base.py
    ├── configuracao.py
    └── workflow.py
```

### 3.1 Organização dos módulos

| Diretório/arquivo | Responsabilidade |
|---|---|
| `__init__.py` | Disponibilizar os principais componentes e funções públicas do SDK. |
| `runtime.py` | Gerenciar a inicialização, recuperação e encerramento do motor de workflow. |
| `aplicacao/` | Concentrar o motor e os componentes responsáveis pela resolução das transições. |
| `configuracao/` | Realizar a leitura, configuração e validação dos arquivos YAML. |
| `dominio/` | Reunir as entidades, o contexto, os resultados e as regras do domínio. |
| `excecoes/` | Organizar as exceções específicas do SDK. |

Essa organização mantém as responsabilidades separadas e facilita a manutenção, a evolução e a reutilização do SDK.

## 4. Componentes arquiteturais

A estrutura do SDK está organizada em módulos que separam configuração, aplicação, domínio, exceções e gerenciamento do runtime.

### 4.1 Runtime

O módulo `runtime` gerencia o ciclo de vida da instância do motor de workflow.

Suas principais responsabilidades são:

- Inicializar o SDK a partir de um arquivo YAML.
- Recuperar a instância configurada do motor.
- Encerrar o runtime quando necessário.

As funções disponibilizadas são:

- `configure()`
- `get_workflow()`
- `shutdown()`

O runtime funciona como ponto de entrada para as aplicações consumidoras que utilizam a instância compartilhada do motor.

### 4.2 Configuração

O pacote `configuracao` é responsável por carregar e validar a configuração declarativa do workflow.

É composto pelas seguintes classes:

| Classe | Responsabilidade |
|---|---|
| `LeitorWorkflow` | Realizar a leitura do arquivo YAML. |
| `ValidadorWorkflow` | Verificar a estrutura e a consistência da configuração. |
| `ConfiguradorWorkflow` | Coordenar o carregamento e a validação da configuração. |

A configuração define os estados disponíveis, as ações permitidas e os respectivos estados de destino.

### 4.3 Aplicação

O pacote `aplicacao` concentra a lógica de execução do motor de workflow.

Seus componentes são:

| Classe | Responsabilidade |
|---|---|
| `MotorWorkflow` | Coordenar a validação e a execução das transições. |
| `DecisaoResolver` | Resolver a decisão configurada para uma ação. |
| `TransicaoResolver` | Resolver as informações da transição entre estados. |

Essa camada utiliza as informações carregadas e validadas na configuração para determinar o resultado de uma operação.

### 4.4 Domínio

O pacote `dominio` reúne as estruturas e regras fundamentais do workflow, sem depender de elementos específicos da aplicação consumidora.

Entre suas principais estruturas estão:

| Classe ou módulo | Responsabilidade |
|---|---|
| `ContextoExecucao` | Representar informações complementares da execução. |
| `ExecucaoValidada` | Representar uma transição que passou pela validação. |
| `ResultadoWorkflow` | Representar o resultado produzido pelo motor. |
| `validacao` | Reunir regras de validação utilizadas pelo domínio. |
| `entidades` | Reunir estruturas de domínio utilizadas pelo SDK. |

### 4.5 Exceções

O pacote `excecoes` organiza as exceções específicas do SDK, permitindo identificar falhas relacionadas à configuração e às operações do workflow.

A separação das exceções facilita o tratamento dos erros pelas aplicações consumidoras.

## 5. Fluxo arquitetural

Esta seção apresenta a comunicação entre a aplicação consumidora e os componentes internos do SDK, desde a inicialização até a utilização do resultado da transição.

### 5.1 Inicialização

```text
Aplicação consumidora
        |
        v
     Runtime
        |
        v
   LeitorWorkflow
        |
        v
  ValidadorWorkflow
        |
        v
   MotorWorkflow
```

O runtime coordena a inicialização, enquanto os componentes de configuração realizam a leitura e a validação do arquivo YAML.

### 5.2 Validação e resolução da transição

```text
Aplicação consumidora
        |
        | Estado atual + ação
        v
   MotorWorkflow
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

A aplicação informa o estado atual e a ação solicitada. O motor valida a operação, resolve a transição configurada e produz o resultado para a aplicação consumidora.

### 5.3 Operações da aplicação consumidora

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
| Validar estrutura do workflow | Sim | Não |
| Controlar estados e transições | Sim | Não |
| Validar ações disponíveis | Sim | Não |
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

Essas funcionalidades podem ser implementadas pelas aplicações consumidoras ou por componentes externos, conforme as necessidades de cada sistema.

## 8. Referências

Para aprofundar o entendimento da implementação e da utilização do SDK, consulte:

- [Primeiros passos](primeiros_passos.md)
- [Configurando o workflow](configurando_workflow.md)
- [Integrando com a aplicação](integrando_aplicacao.md)
- [Tratamento de exceções](tratamento_excecoes.md)
- [Referência da API](api/index.rst)
