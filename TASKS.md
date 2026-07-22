# TASKS.md — Instituto Economia ao Natural
# (ATUALIZAÇÃO: Módulo de Auto-Inscrição em Eventos — itens novos marcados com 🆕)

Este documento divide a implementação do sistema em tarefas menores,
testáveis e incrementais. A ordem de execução recomendada deve ser
estritamente seguida.

---

## FASE 0: PREPARAÇÃO DO AMBIENTE E BANCO DE DADOS
- [x] Configurar Docker para PostgreSQL (Substituído temporariamente por
      SQLite devido a bug insolúvel da libpq do psycopg2 com caracteres
      especiais no path do Windows)
- [x] Ajustar settings.py para ler de .env
- [x] Criar arquivo requirements.txt
- [x] Configurar variável de ambiente DATABASE_URL (Substituída)
- [x] Migrar banco de dados (Tabelas iniciais de Django)

---

## FASE 1: App `accounts`
- [x] **Tarefa 1.1: Criar o App e Definir o Perfil Benegnado**
  - Executar `python manage.py startapp accounts`.
  - Registrar no INSTALLED_APPS.
  - Criar o modelo Benegnado com OneToOneField para User e campos de
    telefone, empresa, cargo e cidade.
  - Registrar o modelo no admin do Django (admin.py).
  - *Verificação:* Rodar makemigrations e migrate. Criar um superusuário
    e validar a criação e edição de um Benegnado pelo Django Admin.
- [x] **Tarefa 1.2: Implementar Autenticação no Frontend
  (Signup/Login/Logout)**
  - Criar as views e formulários de cadastro (signup) com validação de
    dados e login/logout.
  - Criar os templates simples e preliminares para Login, Cadastro e
    Painel Geral.
  - Garantir suporte ao parâmetro `?next=` no login, para 🆕 permitir
    retorno automático à página pública do evento após autenticação
    (necessário para o fluxo de auto-inscrição da Fase 3).
  - *Verificação:* Testar o fluxo completo de auto-cadastro em
    `/accounts/signup/`, logar em `/accounts/login/` e deslogar.

---

## FASE 2: App `people`
- [x] **Tarefa 2.1: Criar o App e o Modelo Benegnador**
  - Executar `python manage.py startapp people`.
  - Registrar no INSTALLED_APPS.
  - Criar o modelo Benegnador (palestrante/facilitador) com nome, email,
    telefone, bio e redes sociais.
  - 🆕 Adicionar campo opcional `user` (OneToOneField para User,
    null=True, blank=True), permitindo que um Benegnador tenha login
    próprio para criar eventos futuramente (Fase 3).
  - Registrar no admin.py com filtros por e-mail e busca por nome.
  - *Verificação:* Executar migrações e testar a criação de múltiplos
    Benegnadores via Django Admin, incluindo um vinculado a um User
    existente.

---

## FASE 3: App `events`
- [x] **Tarefa 3.1: Criar o App e os Modelos de Eventos**
  - Executar `python manage.py startapp events`.
  - Registrar no INSTALLED_APPS.
  - Criar os modelos EventType e Evento.
  - Configurar a relação ManyToMany de Evento com Benegnador (mantida).
  - 🆕 **Não criar** ManyToMany direto de Evento com Benegnado — este
    relacionamento será feito exclusivamente via o novo modelo
    Inscricao (Tarefa 3.3).
  - 🆕 Adicionar em Evento os campos: created_by (FK para User,
    nullable), is_public_enrollment_open (BooleanField, default=True),
    max_participants (PositiveIntegerField, nullable), public_slug
    (SlugField, único).
  - 🆕 Implementar geração automática de public_slug no método save()
    do modelo (a partir de título + data, com slugify e checagem de
    unicidade).
  - *Verificação:* Executar migrações. Criar tipos de eventos (ex.
    "EO") e eventos no Admin, validando que o public_slug é gerado
    automaticamente e é único.
- [x] **Tarefa 3.2: Implementar Propriedades/Métodos de KPIs**
  - Criar a propriedade @property no modelo Evento para calcular
    total_participants e response_rate, 🆕 agora consultando o modelo
    Inscricao (status=CONFIRMED) em vez do M2M direto.
  - 🆕 Criar a propriedade vacancies_left, calculada como
    max_participants - total_participants (retornar None se
    max_participants for nulo).
  - *Verificação:* Rodar testes via Django Shell validando o cálculo
    dessas propriedades com dados mockados, incluindo cenários com e
    sem limite de vagas.
- [x] 🆕 **Tarefa 3.3: Criar o Modelo Inscricao e Regras de Unicidade**
  - Criar o modelo Inscricao com os campos: evento (FK), benegnado (FK),
    status (choices: CONFIRMED, CANCELLED), origin (choices:
    SELF_ENROLLED, ADMIN_ADDED), created_at (auto_now_add).
  - Configurar unique_together = ('evento', 'benegnado').
  - Registrar no Django Admin com inline dentro da tela de Evento
    (TabularInline), permitindo à equipe visualizar e adicionar
    inscrições manualmente (origin=ADMIN_ADDED).
  - *Verificação:* Executar migrações. Tentar criar duas Inscricao para
    o mesmo par evento/benegnado via Admin e validar que o sistema
    impede a duplicidade.
- [x] 🆕 **Tarefa 3.4: Implementar Página Pública do Evento e
  Auto-Inscrição**
  - Criar a view pública `/events/public/<slug:public_slug>/`,
    acessível sem login, exibindo: título, descrição, tipo, data,
    horário, local ou link online (se aplicável), benegnadores
    responsáveis, vagas restantes (se houver limite) e botão
    "Inscrever-se".
  - Se o visitante não estiver autenticado, o botão deve redirecionar
    para login/cadastro com `?next=` apontando de volta para a página
    do evento.
  - Criar a view `/events/enroll/<int:event_id>/` (POST, login
    obrigatório) que: valida is_public_enrollment_open, valida
    vacancies_left (se aplicável), valida ausência de Inscricao prévia,
    cria a Inscricao com origin=SELF_ENROLLED, e dispara e-mail de
    confirmação (integração com Fase 5).
  - Criar a view `/events/unenroll/<int:event_id>/` (POST, login
    obrigatório) que atualiza Inscricao.status=CANCELLED para o par
    evento/benegnado logado, sem excluir o registro.
  - Criar a listagem pública `/events/public/` com todos os eventos que
    possuem is_public_enrollment_open=True e data futura.
  - *Verificação:* Criar um evento de teste com vagas limitadas. Acessar
    a página pública sem estar logado e validar o redirecionamento para
    login. Logar, inscrever-se, e validar a criação da Inscricao e a
    atualização de vacancies_left. Tentar se inscrever novamente e
    validar o bloqueio de duplicidade. Esgotar as vagas e validar que o
    botão de inscrição é desabilitado/ocultado.
  - *Verificação adicional:* Cancelar a inscrição via
    `/events/unenroll/` e validar que o status muda para CANCELLED e
    que vacancies_left é recalculado corretamente.

---

## FASE 4: App `impact_forms`
- [x] **Tarefa 4.1: Criar o App e Modelos de Indicadores**
  - Executar `python manage.py startapp impact_forms`.
  - Criar os modelos: ImpactDimension, ImpactQuestion, ImpactForm,
    ImpactResponse e ImpactAnswer.
  - Configurar a restrição unique_together em ImpactResponse.
  - Registrar os modelos no Django Admin para gerenciar as perguntas e
    visualizar respostas.
  - *Verificação:* Executar migrações e validar criação dos modelos via
    Django Admin.
- [x] **Tarefa 4.2: Popular Questões Padrão via Data Migration**
  - Criar uma migration de dados que insira automaticamente as 4
    dimensões (D1-D4 com pesos padrão) e as 19 perguntas (16 Likert + 3
    abertas) especificadas na especificação de requisitos.
  - *Verificação:* Rodar migrate e verificar no Django Admin que as
    dimensões e questões padrão foram cadastradas automaticamente.
- [x] **Tarefa 4.3: Implementar a View de Resposta ao Formulário**
  - Criar a view `/impact/respond/<form_id>/` que renderiza o formulário
    com as 16 perguntas Likert (botões rádio de 1 a 5) e 3 abertas.
  - 🆕 A checagem de elegibilidade para responder deve considerar se o
    benegnado possui uma Inscricao com status=CONFIRMED no evento
    associado ao ImpactForm (em vez do M2M antigo).
  - Garantir por lógica de banco e view que o usuário só possa enviar
    uma única resposta por formulário.
  - *Verificação:* Testar responder o questionário com um usuário
    logado e inscrito no evento. Validar que as respostas são salvas
    nas tabelas ImpactResponse e ImpactAnswer. Tentar acessar o
    formulário novamente com o mesmo usuário e validar que o sistema
    impede e redireciona para `/impact/success/`. 🆕 Testar também que
    um usuário sem Inscricao=CONFIRMED no evento não consegue acessar o
    formulário.

---

## FASE 5: App `communications`
- [x] **Tarefa 5.1: Criar o App e Modelos de Envio e Tracking**
  - Executar `python manage.py startapp communications`.
  - Criar os modelos EmailLog e EmailTracking.
  - 🆕 Adicionar o choice `ENROLLMENT_CONFIRMATION` ao campo type de
    EmailLog.
  - *Verificação:* Executar migrações e registrar no Django Admin.
- [x] **Tarefa 5.2: Implementar o Tracking de E-mail (Pixel e Clique)**
  - Criar a view de rastreamento do pixel
    (`/communications/track/pixel/<uuid:token>/`) que registra a
    abertura no EmailTracking correspondente e retorna uma imagem PNG
    transparente de 1x1.
  - Criar a view de clique
    (`/communications/track/click/<uuid:token>/`) que grava a data/hora
    do clique no EmailTracking e redireciona o usuário para o destino
    final.
  - *Verificação:* Enviar um e-mail simulado com pixel e links. Acessar
    o endpoint do pixel via navegador e validar no banco de dados se
    opened_at foi preenchido. Clicar no link de redirecionamento e
    validar clicked_at e o redirecionamento.
- [x] **Tarefa 5.3: Implementar o Serviço de Envio e Lembretes
  (django-q2)**
  - Configurar o django-q2 no settings.py.
  - Criar o script/função que envia convites manuais de e-mail a partir
    do painel admin.
  - 🆕 Criar a função `send_enrollment_confirmation(inscricao)`,
    disparada automaticamente logo após a criação de uma Inscricao com
    origin=SELF_ENROLLED (chamada a partir da view de enroll da Fase
    3.4), enviando e-mail de confirmação com os dados do evento.
  - Criar a tarefa periódica/agendada para enviar lembretes automáticos
    de forma condicional (enquanto não houver ImpactResponse para
    aquele participante no evento correspondente, considerando apenas
    Inscricao com status=CONFIRMED).
  - *Verificação:* Executar localmente a fila de tarefas e disparar os
    envios, validando a criação dos registros em EmailLog. 🆕 Validar
    especificamente que, ao criar uma Inscricao via
    `/events/enroll/...`, um EmailLog do tipo ENROLLMENT_CONFIRMATION é
    criado automaticamente.

---

## FASE 6: App `content`
- [x] **Tarefa 6.1: Criar o App e Modelo de Conteúdo**
  - Executar `python manage.py startapp content`.
  - Criar o modelo ContentItem associado obrigatoriamente a um Evento.
  - *Verificação:* Executar migrações e validar criação no Admin.
- [x] **Tarefa 6.2: Implementar Regras de Acesso Seguro**
  - Implementar a view `/content/view/<content_id>/` que checa
    programaticamente se o benegnado autenticado possui uma 🆕
    Inscricao com status=CONFIRMED para o evento do conteúdo (em vez do
    M2M antigo). Caso contrário, retornar erro de permissão (403
    Forbidden).
  - *Verificação:* Testar o acesso com dois participantes diferentes:
    um inscrito no evento via Inscricao=CONFIRMED (deve visualizar o
    conteúdo) e um não inscrito, ou com Inscricao=CANCELLED (deve
    receber erro 403).

---

## FASE 7: App `api` (Django REST Framework)
- [x] **Tarefa 7.1: Configurar DRF e Serializers**
  - Executar `python manage.py startapp api`.
  - Configurar serializers.py para expor Eventos, Benegnados,
    Benegnadores, Formulários e Respostas de Impacto.
  - 🆕 Adicionar InscricaoSerializer, expondo evento, benegnado, status,
    origin e created_at.
  - Criar ViewSets básicas ligadas a rotas em api/urls.py.
  - *Verificação:* Acessar /api/ pelo navegador e testar a visualização
    dos dados serializados na interface navegável do DRF, 🆕 incluindo
    o endpoint de inscrições.

---

## FASE 8: Frontend de Alta Fidelidade (Identidade Visual)
- [x] **Tarefa 8.1: Criar o Sistema de Design CSS (base.css)**
  - Criar o arquivo de estilos global mapeando as cores corporativas
    (Teal #236B86, Ciano #51B0C4, Laranja #F3913A, etc.) e carregando as
    fontes (Bebas Neue / Inter) via Google Fonts.
  - Implementar cartões com bordas arredondadas, gradientes nos
    cabeçalhos e botões com transição suave.
  - *Verificação:* Validar a aparência visual em múltiplos tamanhos de
    tela.
- [x] **Tarefa 8.2: Implementar Telas do Participante**
  - Desenvolver a Home Institucional, tela de Login, Cadastro, Painel de
    Eventos, Página de Questionário Likert e Tela de Materiais.
  - 🆕 Desenvolver a Página Pública do Evento
    (`/events/public/<slug>/`), com destaque visual para o botão
    "Inscrever-se" (cor Laranja Vivo #F3913A) e indicador de vagas
    restantes.
  - 🆕 Desenvolver a Listagem Pública de Eventos
    (`/events/public/`), em formato de cards, seguindo a identidade
    visual (gradiente Teal/Ciano no cabeçalho da página).
  - 🆕 Adicionar ao Painel do Benegnado (`/dashboard/`) uma seção
    "Meus Eventos" mostrando status da inscrição (Confirmada /
    Cancelada) e botão de cancelamento.
  - *Verificação:* Garantir responsividade e concordância com os
    princípios de marca.
- [x] 🆕 **Tarefa 8.3: Implementar Formulário de Criação de Evento para
  Benegnador**
  - Criar a view `/events/create/`, acessível apenas para usuários Staff
    ou Benegnador com login próprio vinculado (via campo user em
    Benegnador).
  - Formulário deve incluir todos os campos de Evento, com geração
    automática do public_slug ao salvar.
  - *Verificação:* Logar como um Benegnador com conta vinculada, criar
    um evento pelo formulário, e validar que ele aparece corretamente
    na listagem pública e que o link gerado funciona para inscrição de
    terceiros.
- [x] **Tarefa 8.4: Implementar o Dashboard de KPIs do Administrador**
  - Criar uma tela customizada acessível apenas para equipe staff em
    `/admin/dashboard-kpi/<event_id>/` exibindo: taxa de resposta e
    contagem de participantes (🆕 agora baseada em Inscricao), média do
    Índice Final (cálculo matemático IIH) e médias por dimensão (D1-D4),
    distribuição de respostas Likert por pergunta, botão de exportação
    de dados para CSV/Excel.
  - 🆕 Adicionar ao dashboard um indicador de vagas restantes e total de
    inscrições canceladas (Inscricao.status=CANCELLED), útil para a
    equipe entender desistências.
  - *Verificação:* Cadastrar dados de teste, calcular os scores
    manualmente e cruzar com o dashboard para conferir precisão
    decimal.

---

## 🆕 Resumo das Alterações Nesta Atualização

- Nova Tarefa 3.3 (modelo Inscricao) e Tarefa 3.4 (página pública +
  auto-inscrição) no app events.
- Tarefa 3.1 ajustada: Evento não terá mais M2M direto com Benegnado;
  novos campos created_by, is_public_enrollment_open, max_participants,
  public_slug.
- Tarefa 3.2 ajustada: KPIs agora consultam Inscricao; nova propriedade
  vacancies_left.
- Tarefa 2.1 ajustada: Benegnador ganha campo opcional user.
- Tarefa 4.3 e 6.2 ajustadas: checagem de acesso via
  Inscricao.status=CONFIRMED em vez do M2M antigo.
- Tarefa 5.1 e 5.3 ajustadas: novo tipo de e-mail
  ENROLLMENT_CONFIRMATION e disparo automático ao se inscrever.
- Tarefa 7.1 ajustada: novo InscricaoSerializer.
- Tarefa 8.2 ajustada e nova Tarefa 8.3: telas públicas de evento,
  listagem pública, seção "Meus Eventos" no dashboard, e formulário de
  criação de evento para Benegnador.

---

## 🆕 FASE 9: Ferramentas Administrativas e Integração Avançada
- [x] **Tarefa 9.1: Importação de Participantes em Massa**
  - Criação do comando de gerenciamento `import_participants` (via CLI).
  - Leitura de arquivo CSV, criação automática de contas de usuário (com senha padrão) e vínculos (Inscricao=CONFIRMED) no evento.
- [x] **Tarefa 9.2: Disparo de Lembretes e Tracking pelo Painel**
  - Criação da view `event_responses_dashboard` (Lembretes & Respostas).
  - Identificação de inscritos que ainda não responderam ao formulário.
  - Envio em massa e assíncrono de e-mails (usando `django-q2` e URL única rastreável) e link direto no admin do evento.
- [x] **Tarefa 9.3: Customização da Identidade Visual do Django Admin**
  - Sobrescrita do `base_site.html` do Admin para aplicar a paleta de cores corporativa (Teal/Laranja) e fontes.
  - Adição da logo da marca na tela de login e cabeçalho interno do Admin.

---

## 🆕 FASE 10: Frontend Institucional Soft UI, App de Blog e Dashboard Integrado
- [x] **Tarefa 10.1: Sistema de Design Soft UI e Páginas Institucionais**
  - Implementação do `base.css` com variáveis de cores institucionais (Teal #236B86, Ciano #51B0C4, Laranja #F3913A), tipografias Google Fonts (Bebas Neue / Inter), sombras suaves e border-radius.
  - Criação do template base (`base.html`) com navbar responsiva, menu dropdown suspenso para usuários autenticados e rodapé.
  - Criação da página Home (`home.html`) com hero section em gradiente, blocos de pilares e destaque de eventos.
  - Criação da página Sobre (`sobre.html`) com layout acolhedor e formas orgânicas customizadas via `clip-path`.
- [x] **Tarefa 10.2: Novo App `blog` com Editor WYSIWYG**
  - Criação da aplicação Django `blog` com modelo `Post` (Título, Slug, Conteúdo HTML, Autor, Imagem de Capa, Status).
  - Implementação de permissões granulares (`StaffOrBenegnadorRequiredMixin`) para restrição de criação e edição.
  - Integração do editor leve WYSIWYG **Summernote Lite** via CDN no formulário de criação/edição.
  - Criação dos templates de listagem (`post_list.html`), leitura amigável (`post_detail.html`), formulário (`post_form.html`) e exclusão (`post_confirm_delete.html`).
- [x] **Tarefa 10.3: Reformulação das Páginas Públicas de Eventos**
  - Atualização da view `public_event_list` e template `public_list.html` dividindo em duas seções: Eventos Ativos (com vagas dinâmicas e CTA Laranja) e Eventos Encerrados (estilo opaco em escala de cinza e botão desabilitado).
  - Atualização do template `public_detail.html` com confirmação de inscrição e link direto para o Painel do Membro.
- [x] **Tarefa 10.4: Painel do Membro Integrado com KPIs de Impacto**
  - Reformulação visual do Dashboard (`/dashboard/`) para participantes, facilitadores e administradores.
  - Integração de relatórios de KPIs em tempo real (IIH Geral, Respostas, Cancelamentos e Dimensões de Impacto) diretamente na área logada do site para Staff e Benegnadores.