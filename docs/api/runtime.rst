Runtime
=======

O módulo ``runtime`` é responsável por gerenciar o ciclo de vida do SDK de workflow na aplicação consumidora.

Por meio dele, a aplicação pode inicializar o SDK a partir de um arquivo YAML, obter acesso à instância compartilhada do motor de workflow e encerrar sua utilização quando necessário.

Para isso, o módulo disponibiliza funções que centralizam o carregamento, a validação e a inicialização da configuração, garantindo que o motor esteja pronto para ser utilizado pela aplicação.

A seguir, são apresentadas as responsabilidades do módulo e as funções disponibilizadas para integração com a aplicação consumidora.

.. automodule:: sme_workflow_sdk.runtime
   :members:
   :undoc-members:
   :show-inheritance:
