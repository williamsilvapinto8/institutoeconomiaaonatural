# PROJECT.md — Instituto Economia ao Natural
# (ATUALIZAÇÃO: Módulo de Auto-Inscrição em Eventos — itens novos marcados com 🆕)

> [!NOTE]
> **Status:** Todas as fases descritas neste documento foram implementadas com sucesso (incluindo as novidades marcadas com 🆕).

Este documento descreve a arquitetura completa do sistema para a plataforma do
Instituto Economia ao Natural, contemplando o modelo de dados, as rotas
principais, fluxos de negócios, stack técnica e a estratégia de implantação
(deploy) em uma VPS Hostinger de baixo custo.

---

## 1. Stack Técnica Detalhada

- Linguagem: Python 3.11+
- Framework Web: Django 5.x (versão estável)
- Banco de Dados: PostgreSQL 15+
- Controle de Ambiente: virtualenv, python-decouple ou django-environ
  (gerenciamento de variáveis via .env), requirements.txt.
- Frontend: Django Templates + CSS nativo + Bootstrap 5.3 (aplicando a
  paleta de cores institucional e tipografia Bebas Neue/Inter).
- APIs: Django REST Framework (DRF) para expor serializers e endpoints
  básicos (prontos para expansão futura).
- Servidor de Produção: Nginx como proxy reverso + Gunicorn como servidor
  de aplicação WSGI + PostgreSQL como banco de dados.

### 1.1. Decisão Técnica: Motor de Agendamento (Scheduler)

Para o agendamento de convites e lembretes automáticos em uma VPS de poucos
recursos, analisamos três alternativas:

1. Celery + Redis: requer dois daemons persistentes rodando em segundo
   plano. Consome cerca de 150MB+ de RAM adicionais. Excelente para grandes
   volumes, mas pesado para este cenário.
2. django-q2 (ORM Backend): roda tarefas usando o próprio PostgreSQL como
   fila. Requer o processo qcluster ativo. Robusto, com painel integrado
   no Django Admin.
3. Cron do Sistema (Linux) + Django Management Commands: script disparado
   periodicamente pelo cron. Consome 0MB de RAM quando ocioso.

Decisão: utilizaremos django-q2 com banco de dados (ORM) como opção padrão
para agendamentos assíncronos, combinada com a facilidade de configurar um
Command + Cron para otimização extrema de memória. No Django Admin, a
equipe poderá visualizar os logs e status dos disparos de forma simples.

---

## 2. Estrutura de Apps Django (Modular)

O projeto será dividido em 7 apps independentes, cada uma com
responsabilidade única:

### 2.1. App `accounts`

Responsável pela autenticação e pelo perfil de usuário do participante
("Benegnado").

- Diferenciação de Perfis:
  - Equipe do Instituto (Staff/Superuser): acessa o Django Admin padrão.
  - Benegnados: usuários finais com login no painel restrito para
    responder formulários, visualizar conteúdos e 🆕 se inscrever em
    eventos públicos.
- Modelos:
  - `Benegnado`:
    - user (OneToOneField com o User padrão do Django)
    - phone (CharField, para celular/WhatsApp)
    - company (CharField, opcional, para eventos in-company)
    - role (CharField, opcional)
    - city (CharField, opcional)

### 2.2. App `people`

Gerenciamento de facilitadores e palestrantes do Instituto ("Benegnadores").

- Modelos:
  - `Benegnador`:
    - name (CharField)
    - email (EmailField, único)
    - phone (CharField)
    - bio (TextField, opcional)
    - linkedin_url (URLField, opcional)
    - instagram_url (URLField, opcional)
    - 🆕 user (OneToOneField com User, nullable) — permite que um
      Benegnador também tenha login próprio para criar eventos
      diretamente pela plataforma (ver seção 2.3).

### 2.3. App `events`

Responsável pela gestão de locais, datas, inscrições e 🆕 auto-inscrição
pública dos eventos.

- Modelos:
  - `EventType`:
    - name (CharField, único — ex: "Comunidade", "In Company", "Imersão",
      "EO")
  - `Evento`:
    - title (CharField)
    - description (TextField)
    - event_type (ForeignKey para EventType)
    - date (DateField)
    - start_time (TimeField)
    - end_time (TimeField)
    - location (CharField)
    - is_online (BooleanField)
    - online_platform (CharField, opcional — ex: Zoom, Teams, Meet)
    - online_link (URLField, opcional)
    - benegnadores (ManyToManyField com people.Benegnador)
    - 🆕 created_by (ForeignKey para User, nullable) — registra se o
      evento foi criado por um Admin/Staff ou por um Benegnador com
      login próprio.
    - 🆕 is_public_enrollment_open (BooleanField, default=True) —
      controla se o botão/link de auto-inscrição está ativo. O admin ou
      o benegnador criador podem desativar quando as vagas se esgotarem
      ou o evento já tiver ocorrido.
    - 🆕 max_participants (PositiveIntegerField, nullable) — limite
      opcional de vagas. Se nulo, inscrições ilimitadas.
    - 🆕 public_slug (SlugField, único, gerado automaticamente a partir
      do título + data) — usado para montar a URL pública de divulgação
      do evento.
    - ~~benegnados (ManyToManyField com accounts.Benegnado)~~ 🆕
      **removido como M2M direto** e substituído pelo modelo
      intermediário `Inscricao` (ver abaixo), pois agora precisamos
      registrar status, data e origem da inscrição — informação que um
      ManyToMany simples não comporta.
  - 🆕 `Inscricao` (novo modelo — substitui o M2M direto
    Evento.benegnados):
    - evento (ForeignKey para Evento, related_name='inscricoes')
    - benegnado (ForeignKey para accounts.Benegnado,
      related_name='inscricoes')
    - status (CharField, choices: `CONFIRMED`, `CANCELLED` —
      default=CONFIRMED)
    - origin (CharField, choices: `SELF_ENROLLED` [inscrito pelo próprio
      participante via link público], `ADMIN_ADDED` [adicionado
      manualmente pela equipe/benegnador] — default=SELF_ENROLLED)
    - created_at (DateTimeField, auto_now_add)
    - Restrição: unique_together = ('evento', 'benegnado') — impede
      inscrição duplicada no mesmo evento.
- Propriedades de KPI (ORM):
  - total_participants: contagem de Inscricao com status=CONFIRMED para
    o evento (substituindo a contagem antiga via M2M).
  - response_rate: percentual de benegnados inscritos (via Inscricao)
    que criaram um ImpactResponse para este evento.
  - 🆕 vacancies_left: calculado como
    `max_participants - total_participants` (quando max_participants não
    é nulo); usado para exibir "X vagas restantes" na página pública.

### 2.4. App `impact_forms`

Gerenciamento das dimensões de impacto humano (IIH), questionários Likert
e respostas. (Sem alterações nesta atualização — mantido conforme
especificação anterior: ImpactDimension, ImpactQuestion, ImpactForm,
ImpactResponse, ImpactAnswer, com unique_together em ImpactResponse.)

### 2.5. App `communications`

Rastreamento e envio de convites e lembretes automáticos.

- Modelos: `EmailLog`, `EmailTracking` (sem alterações estruturais).
- 🆕 Novo gatilho de envio: ao criar uma `Inscricao` com
  origin=SELF_ENROLLED, disparar automaticamente um e-mail de confirmação
  de inscrição (type=`ENROLLMENT_CONFIRMATION`, novo choice em
  EmailLog.type) informando data, local/link e próximos passos.

### 2.6. App `content`

Gerenciamento de conteúdos complementares pós-evento restritos aos
participantes inscritos.

- Modelos: `ContentItem` (sem alterações estruturais). A regra de acesso
  agora verifica a existência de uma `Inscricao` com status=CONFIRMED
  entre o benegnado e o evento do conteúdo, em vez do M2M direto.

### 2.7. App `api`

Módulo para disponibilização de serializers e endpoints básicos usando
Django REST Framework.

- Classes Básicas: BenegnadoSerializer, BenegnadorSerializer,
  EventoSerializer, ImpactFormSerializer, ImpactResponseSerializer,
  🆕 InscricaoSerializer.

### 2.8. 🆕 App `blog`

Módulo completo para publicação e gestão de artigos e pesquisas sobre economia regenerativa.

- Modelos:
  - `Post`:
    - title (CharField)
    - slug (SlugField único, gerado via slugify)
    - content (TextField em formato HTML Rich Text)
    - author (ForeignKey para User)
    - cover_image (ImageField, opcional)
    - is_published (BooleanField, default=True)
    - created_at / updated_at (DateTimeField)
- Permissões:
  - Visualização pública dos artigos.
  - Criação, edição e exclusão restritas via `@staff_or_benegnador_required` e `StaffOrBenegnadorRequiredMixin` para usuários Staff e Benegnadores.
- Editor Integrado:
  - Summernote Lite via CDN no formulário de postagem para edição WYSIWYG leve sem depender de pacotes pesados no backend.

---

## 3. Rotas Principais do Sistema
ÁREA PÚBLICA:
├── / -> Home Institucional
├── /sobre/ -> Página Sobre o Instituto (Design Orgânico)
├── /accounts/login/ -> Login de Benegnados
├── /accounts/signup/ -> Auto-cadastro de Benegnados
├── /events/public/<slug>/ -> Página pública do evento (detalhes e inscrição)
├── /events/public/ -> Listagem pública de eventos (Ativos vs Encerrados)
├── /blog/ -> Listagem pública de artigos do Blog
└── /blog/<slug>/ -> Leitura do artigo

ÁREA DO BENEGNADO (Autenticado):
├── /dashboard/ -> Painel do Membro (Inscrições + KPIs de Impacto para Gestores)
├── /events/enroll/<int:event_id>/ -> Ação de inscrição (POST)
├── /events/unenroll/<int:event_id>/ -> Ação de cancelamento de inscrição
├── /impact/respond/<form_id>/ -> Formulário de avaliação de impacto humano
├── /impact/success/ -> Tela de agradecimento pós-resposta
└── /content/view/<content_id>/ -> Visualização segura do material do evento

ÁREA DO BENEGNADOR / STAFF (Autenticado):
├── /events/create/ -> Formulário de criação de evento
├── /blog/novo/ -> Formulário de criação de artigo no Blog (Editor WYSIWYG)
├── /blog/<slug>/editar/ -> Formulário de edição de artigo
└── /blog/<slug>/deletar/ -> Confirmação e exclusão de artigo

ÁREA ADMINISTRATIVA (Customizada & Django Admin):
├── /admin/ -> Painel administrativo padrão Django customizado
└── /admin/dashboard-kpi/<event_id>/ -> Dashboard estatístico de KPIs por evento

RASTREAMENTO DE COMUNICAÇÕES (Endpoints Técnicos): ├── /communications/track/pixel// -> Pixel de abertura de │ email (retorna PNG 1x1) └── /communications/track/click// -> Redirecionamento e registro de clique

---

## 4. Fluxos Críticos do Sistema

### 4.1. 🆕 Fluxo de Criação de Evento e Geração de Link Público

1. Criação: um usuário Staff (via Django Admin) ou um Benegnador com login
   próprio (via `/events/create/`) preenche os dados do evento (título,
   descrição, tipo, data, local ou link online, vagas máximas opcionais).
2. Geração automática do slug: ao salvar, o sistema gera `public_slug` a
   partir do título + data (ex.: `imersao-eo-abril-2026-12-04`),
   garantindo unicidade.
3. Publicação: o evento passa a estar acessível publicamente em
   `/events/public/<public_slug>/`, mesmo para visitantes não logados
   (que verão os detalhes, mas precisarão logar/cadastrar-se para
   concluir a inscrição).
4. Divulgação: a equipe do Instituto ou o Benegnador compartilha o link
   público (WhatsApp, e-mail, redes sociais).

### 4.2. 🆕 Fluxo de Auto-Inscrição do Participante

1. Acesso à página pública: o visitante acessa
   `/events/public/<public_slug>/` e vê os detalhes do evento (tema,
   data, horário, local/link online, benegnadores responsáveis, vagas
   restantes se aplicável) e um botão "Inscrever-se".
2. Autenticação: se o visitante não estiver logado, o clique no botão
   redireciona para `/accounts/login/?next=/events/public/.../` ou para
   o cadastro, preservando o destino após autenticação bem-sucedida.
3. Confirmação da inscrição: uma vez autenticado, o clique em
   "Inscrever-se" dispara um POST para
   `/events/enroll/<int:event_id>/`, que:
   - Verifica se `is_public_enrollment_open=True`.
   - Verifica se há vagas (`vacancies_left > 0`, se `max_participants`
     não for nulo).
   - Verifica se já não existe uma `Inscricao` prévia para aquele par
     evento/benegnado (impedindo duplicidade via unique_together).
   - Cria a `Inscricao` com origin=SELF_ENROLLED e status=CONFIRMED.
   - Dispara e-mail de confirmação de inscrição (via app
     communications).
4. Retorno: o usuário é redirecionado de volta à página do evento (ou ao
   seu `/dashboard/`) com uma mensagem de sucesso ("Inscrição realizada
   com sucesso! Você receberá um e-mail de confirmação.").
5. Cancelamento (opcional): o benegnado pode cancelar sua própria
   inscrição a partir do `/dashboard/`, o que aciona
   `/events/unenroll/<int:event_id>/` e atualiza
   `Inscricao.status=CANCELLED` (sem excluir o registro, preservando
   histórico).

### 4.3. Fluxo de Resposta do Questionário de Impacto

(Mantido conforme especificação anterior.) O Benegnado autenticado acessa
`/impact/respond/ID/`; a view verifica ImpactResponse existente; caso
contrário, renderiza as 16 perguntas fechadas + 3 abertas; ao submeter,
cria ImpactResponse + ImpactAnswer em transação; redireciona para
`/impact/success/`.

### 4.4. Rastreamento de E-mails (Tracking de Abertura e Clique)

(Mantido conforme especificação anterior — pixel de abertura e redirect
com registro de clique.)

---

## 5. Algoritmo de Cálculo do IIH (Indicador de Impacto Humano)

(Mantido integralmente conforme especificação anterior — sem alterações
nesta atualização.)

1. Pontuação por Dimensão (D1 a D4): média aritmética das respostas
   Likert das perguntas daquela dimensão.
2. Cálculo do Índice Final do Respondente (IF): soma ponderada das
   pontuações de cada dimensão multiplicada por 20.
3. Métricas do Painel KPI do Evento: média global do Índice Final, média
   por dimensão, distribuição de frequências por pergunta.

---

## 6. Plano de Deploy na VPS Hostinger

(Mantido integralmente conforme especificação anterior — provisionamento
Ubuntu 22.04, PostgreSQL, Nginx, Gunicorn via systemd, Certbot para SSL,
cron para `process_scheduled_emails`.)

---

## 7. 🆕 Resumo das Alterações Nesta Atualização

- Novo modelo `Inscricao` (app events), substituindo o ManyToMany direto
  `Evento.benegnados`, com campos de status, origem e data.
- Novos campos em `Evento`: created_by, is_public_enrollment_open,
  max_participants, public_slug.
- Novo campo opcional em `Benegnador`: user (permite login próprio para criação de eventos).
- Novas rotas públicas para listagem e visualização de evento, e novas rotas autenticadas para inscrição/cancelamento.
- Novo gatilho de e-mail automático de confirmação de inscrição.
- Regras de acesso a conteúdo (`content`) e cálculo de KPIs (`events`)
  passam a se basear em `Inscricao.status=CONFIRMED` em vez do M2M direto.
- **Integração de Admin Avançada:** 
  - Comando CLI para importação de CSV (`import_participants`).
  - Painel de Lembretes no admin com envio assíncrono em massa (`django-q2`).
  - Identidade visual do admin do Django 100% customizada.
- **Frontend Institucional Soft UI & Novo Motor de Blog:**
  - Sistema de Design Soft UI com paleta Teal/Ciano/Laranja e tipografia Bebas Neue e Inter.
  - Páginas institucionais de alta conversão: Home (`/`) e Sobre (`/sobre/`).
  - Novo App `blog` com modelo `Post`, CRUD completo e integração com editor WYSIWYG Summernote Lite via CDN.
  - Reformulação da listagem pública de eventos (`/events/public/`) dividida entre Eventos Ativos e Eventos Encerrados.
  - Reformulação do Painel do Membro (`/dashboard/`) com cartões visuais de KPIs em tempo real (IIH, Média por Dimensão, Respostas e Cancelamentos) para gestores e administradores.

---

## 8. Como Rodar o Projeto Localmente (Desenvolvimento)

Para iniciar o ambiente de desenvolvimento local e rodar o projeto na sua máquina, siga os passos abaixo (no terminal da pasta `dev`):

1. **Ative o ambiente virtual:**
   ```powershell
   .\venv\Scripts\activate
   ```
   *(Nota: Caso utilize o outro ambiente virtual disponível, substitua por `.\venv313\Scripts\activate`)*

2. **Inicie o servidor local do Django:**
   ```powershell
   python manage.py runserver
   ```

3. **Acesse no navegador:**
   Abra o link `http://127.0.0.1:8000/` para visualizar o sistema.