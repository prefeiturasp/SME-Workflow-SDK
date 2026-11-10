Camada de Aplicação
===================

O pacote ``aplicacao`` contém os componentes responsáveis por coordenar
a validação das ações e a resolução das transições do workflow.

A camada é composta por três componentes principais:

* **MotorWorkflow:** coordena o processamento do workflow.
* **DecisaoResolver:** verifica se o estado existe e se a ação solicitada
  está disponível.
* **TransicaoResolver:** valida a transição configurada e seu estado
  de destino.

MotorWorkflow
-------------

.. autoclass:: sme_workflow_sdk.aplicacao.motor_workflow.MotorWorkflow
   :members:
   :undoc-members:
   :show-inheritance:

DecisaoResolver
---------------

.. autoclass:: sme_workflow_sdk.aplicacao.decisao_resolver.DecisaoResolver
   :members:
   :undoc-members:
   :show-inheritance:

TransicaoResolver
-----------------

.. autoclass:: sme_workflow_sdk.aplicacao.transicao_resolver.TransicaoResolver
   :members:
   :undoc-members:
   :show-inheritance:
