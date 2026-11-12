.. py:module:: sme_workflow_sdk.configuracao

Configuração
============

O pacote ``configuracao`` reúne os componentes responsáveis por carregar
e validar os arquivos YAML utilizados na definição dos workflows.

O processo de configuração é dividido em três responsabilidades:

* **ConfiguradorWorkflow:** coordena o carregamento e a validação.
* **LeitorWorkflow:** realiza a leitura do arquivo YAML e verifica sua
  estrutura básica.
* **ValidadorWorkflow:** verifica a estrutura e a consistência dos estados,
  ações e transições configurados.

ConfiguradorWorkflow
--------------------

.. autoclass:: sme_workflow_sdk.configuracao.configurador.ConfiguradorWorkflow
   :members:
   :undoc-members:
   :show-inheritance:

LeitorWorkflow
--------------

.. autoclass:: sme_workflow_sdk.configuracao.leitor.LeitorWorkflow
   :members:
   :undoc-members:
   :show-inheritance:
   :private-members:

ValidadorWorkflow
-----------------

.. autoclass:: sme_workflow_sdk.configuracao.validador.ValidadorWorkflow
   :members:
   :undoc-members:
   :show-inheritance:
   :private-members:
