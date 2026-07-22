# Manual 06: Gestão de Arquivos e Controle de Acesso (Content)

Este manual documenta a regra de negócio para a distribuição de materiais educativos do projeto.

## 1. Cadastrando um Arquivo de Conteúdo
1. O administrador (Staff) acessa o Django Admin (`/admin/`).
2. Entra no módulo **CONTENT** e clica em Adicionar **Content Items** (Itens de Conteúdo).
3. O administrador deve preencher:
   - **Título** do material (ex: Apresentação de Slides PDF).
   - **Evento Relacionado**: É obrigatório associar o arquivo a um Evento existente.
   - **Arquivo**: Faz o upload do documento.
   - **Link Externo**: (Opcional) se o arquivo for hospedado externamente ou for um link do YouTube.
4. Salvar.

## 2. Acesso e Proteção de Download
Quando um usuário comum tentar acessar a URL direta do conteúdo (`/content/view/<id>/`):
1. O sistema verifica primeiro se o usuário está logado. (Senão, exige login).
2. Em seguida, o sistema busca em qual Evento aquele arquivo foi cadastrado.
3. O sistema valida se o usuário solicitante está contido na lista de **Participantes (Benegnados)** daquele Evento.
4. Se sim, a página será exibida contendo o botão de visualização/download.
5. Se não, o sistema retornará imediatamente um erro **403 - Permission Denied** (Acesso Negado), protegendo a propriedade intelectual do material contra usuários não autorizados ou participantes de outras turmas.
