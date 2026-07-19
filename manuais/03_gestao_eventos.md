# Manual 03: Gestão de Eventos e Inscrições

Este manual orienta a criação de novos Eventos e a vinculação de Palestrantes (Benegnadores) e Participantes (Benegnados) aos mesmos.

## 1. Criação de Tipos de Eventos
1. No Painel Admin (`http://localhost:8000/admin/`), localize a seção **EVENTS**.
2. Clique em **Adicionar** ao lado de **Tipos de Evento** (Event Types).
3. Informe o nome da categoria (ex: "Workshop", "Palestra", "Webinar") e clique em **Salvar**.

## 2. Criação de um Novo Evento
1. Volte ao menu principal do Admin e clique em **Adicionar** ao lado de **Eventos**.
2. Preencha as Informações Básicas:
   - **Título**: Nome do Evento (ex: "Oficina de Economia Circular").
   - **Descrição**: Detalhes do evento.
   - **Tipo**: Selecione um tipo na lista suspensa (ou adicione um novo clicando no ícone verde de `+`).
   - **Data, Início e Término**: Defina calendário e horários.
   - **Local / Online**: Insira o local físico ou marque a caixa **Online?** inserindo link e plataforma, se for o caso.

## 3. Inscrição de Palestrantes e Participantes (Relacionamento ManyToMany)
1. Role a página do Evento para baixo até encontrar as duas caixas de seleção dupla.
2. **Benegnadores**: Na caixa da esquerda, selecione os Palestrantes que conduzirão o evento e clique na setinha para a direita para movê-los para a caixa de "Escolhidos".
3. **Participantes (Benegnados)**: Na caixa da esquerda, pesquise (usando a lupa/filtro) ou selecione os alunos/participantes que estão inscritos neste evento. Mova-os para a caixa da direita.
4. Clique em **Salvar** no canto inferior da tela.

> **Nota:** Apenas os usuários inseridos na caixa de **Participantes (Benegnados)** terão acesso ao formulário de impacto e aos materiais daquele evento.
