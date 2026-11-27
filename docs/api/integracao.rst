.. py:module:: sme_workflow_sdk.integracao

Integração
==========

O pacote ``integracao`` disponibiliza os recursos utilizados pela aplicação
consumidora para declarar métodos associados aos estados e às ações do
workflow. Ele reúne o decorator ``@workflow`` e o registro centralizado das
declarações.

A declaração feita pelo decorator não transfere ao SDK a execução das regras
de negócio. O método decorado continua pertencendo à aplicação consumidora,
que também é responsável por importar os módulos que contêm essas declarações.

Decorator ``workflow``
----------------------

O decorator associa um método a uma combinação de estado e ação. Ele recebe os
parâmetros nomeados ``estado`` e ``acao``.

Na chamada do método, a aplicação deve informar o estado por argumento
nomeado.

O decorator consome o argumento ``estado`` para compará-lo com o estado
declarado. Esse argumento não é repassado ao método original e, portanto, não
deve fazer parte da assinatura do método decorado.

Se o estado recebido for diferente do estado declarado, o decorator lança
``EstadoWorkflowIncompativelError``. Se for compatível, a chamada é encaminhada
ao método original. A validação realizada pelo decorator não verifica se a
ação está configurada no YAML nem resolve a transição; essa validação é feita
pelo motor quando a aplicação solicita o processamento da transição.

.. automodule:: sme_workflow_sdk.integracao.decorators
   :members:
   :undoc-members:
   :show-inheritance:

Registro de ações
-----------------

O módulo ``registro_acoes`` mantém as associações entre o par
``(estado, acao)`` e a função original declarada pelo decorator. O registro não
instancia classes da aplicação consumidora.

O registro acontece quando o Python importa o módulo que contém o método
decorado, pois é nesse momento que o decorator é executado. O SDK não realiza
descoberta ou importação automática dos módulos da aplicação. A aplicação deve
assegurar que os módulos com declarações ``@workflow`` sejam importados antes
de chamar os respectivos métodos.

Uma mesma ação pode ser declarada em estados diferentes. Para uma mesma
combinação de estado e ação, o registro não permite substituir um método por
outro. O registro da mesma função para a mesma combinação é idempotente.

A existência de uma declaração no registro não é verificada contra o YAML
durante ``configure()``. A configuração YAML é carregada e validada na
inicialização; a validade da transição solicitada é verificada pelo motor no
momento em que ``processar_transicao()`` é chamado.

.. autoclass:: sme_workflow_sdk.integracao.registro_acoes.RegistroAcoes
   :members:
   :undoc-members:
   :show-inheritance:

Instância compartilhada
-----------------------

O módulo disponibiliza uma instância compartilhada do registro, utilizada pelo
decorator para centralizar as declarações:

.. autodata:: sme_workflow_sdk.integracao.registro_acoes.registro_acoes
   :annotation:
