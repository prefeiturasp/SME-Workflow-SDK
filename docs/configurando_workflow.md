# Configurando workflows

O SME Workflow SDK utiliza arquivos YAML para definir a estrutura e as regras de transição de um workflow.

A configuração descreve os estados disponíveis, as ações permitidas em cada estado e os respectivos estados de destino. A partir dessas informações, o SDK consegue validar se uma transição é permitida e produzir o resultado da execução.

## Estrutura do arquivo

A configuração deve possuir o campo `estados` na raiz do arquivo YAML.

Cada estado define suas ações e, para cada ação, o estado de destino e a indicação de terminalidade.

```yaml
estados:
  nome_do_estado:
    acoes:
      nome_da_acao:
        proximo_estado: nome_do_proximo_estado
        terminal: false
```

A estrutura possui três elementos principais:

| Elemento | Descrição |
|---|---|
| `estados` | Agrupa todos os estados definidos no workflow. |
| `acoes` | Define as ações disponíveis em determinado estado. |
| `proximo_estado` | Identifica o estado para o qual a transição será direcionada. |
| `terminal` | Indica se o estado de destino é terminal. |

## Definindo estados

Os estados representam as etapas pelas quais uma entidade pode passar durante seu ciclo de vida.

Cada estado deve possuir um nome válido e uma configuração de ações.

Exemplo:

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

  aprovado:
    acoes: null
```

Nesse exemplo, o workflow possui três estados:

- `rascunho`: permite enviar a solicitação para análise.
- `aguardando_analise`: permite aprovar a solicitação.
- `aprovado`: representa o encerramento do workflow.

## Definindo ações

As ações representam as operações permitidas a partir de determinado estado.

Cada ação deve possuir obrigatoriamente dois campos:

- `proximo_estado`: nome do estado de destino.
- `terminal`: valor booleano que indica se o destino é terminal.

Exemplo:

```yaml
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
```

Nesse exemplo, o estado `aguardando_analise` disponibiliza três ações diferentes, cada uma direcionando o workflow para um estado específico.

## Transições e estados de destino

Uma transição representa a passagem de um estado atual para outro por meio de uma ação.

O campo `proximo_estado` deve referenciar um estado existente na configuração.

Exemplo:

```yaml
estados:
  pendente:
    acoes:
      iniciar:
        proximo_estado: em_andamento
        terminal: false

  em_andamento:
    acoes:
      concluir:
        proximo_estado: concluido
        terminal: true

  concluido:
    acoes: null
```

Nesse fluxo:

1. O workflow inicia em `pendente`.
2. A ação `iniciar` direciona para `em_andamento`.
3. A ação `concluir` direciona para `concluido`.
4. O estado `concluido` encerra o workflow.

O SDK verifica se o estado de destino existe e se a transição respeita as regras de consistência da configuração.

## Estados terminais

Um estado terminal representa o encerramento do workflow. Ele não disponibiliza novas ações.

Para definir um estado terminal, a ação que direciona para ele deve possuir `terminal: true`.

O estado de destino deve possuir `acoes: null`.

Exemplo:

```yaml
estados:
  aguardando_aprovacao:
    acoes:
      aprovar:
        proximo_estado: aprovado
        terminal: true

  aprovado:
    acoes: null
```

Nesse caso, `aprovado` é um estado terminal e não permite novas transições.

## Estados não terminais

Um estado não terminal permite a continuidade do workflow e, portanto, deve possuir pelo menos uma ação disponível.

As ações que direcionam para estados não terminais devem possuir `terminal: false`.

Exemplo:

```yaml
estados:
  aguardando_analise:
    acoes:
      solicitar_ajustes:
        proximo_estado: em_ajuste
        terminal: false

  em_ajuste:
    acoes:
      reenviar:
        proximo_estado: aguardando_analise
        terminal: false
```

Nesse exemplo, o workflow permite retornar para análise após a realização dos ajustes.

## Exemplo completo

A seguir, um exemplo de workflow que representa o processo de análise de uma solicitação.

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

O fluxo permite que uma solicitação seja enviada para análise, aprovada, reprovada ou devolvida para ajustes.

Após a realização dos ajustes, a solicitação pode retornar para análise.

## Regras de validação

O SDK realiza verificações estruturais e de consistência na configuração do workflow definida no arquivo YAML.

As principais regras são:

### Estrutura geral

- A configuração deve possuir a seção `estados`.
- A seção `estados` deve conter pelo menos um estado.
- Os nomes dos estados devem ser válidos.

### Estados e ações

- Cada estado deve possuir a propriedade `acoes`.
- A propriedade `acoes` deve conter uma ou mais ações ou receber o valor `null`.
- Quando informadas, as ações não podem estar vazias.
- Os nomes das ações devem ser válidos.
- Cada ação deve possuir as propriedades `proximo_estado` e `terminal`.
- Não são permitidas propriedades adicionais na definição de uma ação.

### Transições

- A propriedade `proximo_estado` deve possuir um valor válido.
- O estado de destino deve existir na configuração.
- A propriedade `terminal` deve receber um valor booleano (`true` ou `false`).
- Uma transição não terminal não pode apontar para o próprio estado.
- Um estado terminal deve possuir `acoes: null`.
- Um estado não terminal deve possuir ações disponíveis.

Caso alguma dessas regras não seja atendida, o SDK lança a exceção correspondente à validação que falhou.

## Validando a configuração

A leitura e a validação do arquivo YAML devem ser realizadas por meio da função `configure()`, disponibilizada pelo SDK.

Para inicializar o SDK, basta informar o caminho do arquivo de configuração:

```python
from sme_workflow_sdk import configure

configure("workflow.yaml")
```

Ao executar `configure()`, o SDK realiza internamente as seguintes operações:

1. **Carregamento:** lê o arquivo YAML informado e converte seu conteúdo para a estrutura interna utilizada pela biblioteca.
2. **Validação:** verifica a estrutura e a consistência da configuração, incluindo estados, ações e transições.
3. **Inicialização:** disponibiliza o runtime com o motor de workflow configurado para utilização pela aplicação.

Caso o arquivo não seja encontrado ou alguma regra de validação não seja atendida, o SDK lança a exceção correspondente.

Não é necessário instanciar diretamente `ConfiguradorWorkflow` nem chamar seus métodos `carregar()` e `validar()`, pois essas operações são executadas internamente por `configure()`.

## Próximos passos

- [Primeiros passos](primeiros_passos)
- [Integração com a aplicação](integrando_aplicacao)
- [Tratamento de exceções](tratamento_excecoes)
- [Referência da API](api/index)
