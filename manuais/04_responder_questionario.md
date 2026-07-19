# Manual 04: Questionário de Impacto

Este manual explica como o participante responde ao formulário de percepção e medição de impacto após o evento.

## 1. Visualização de Pendências no Dashboard
1. O participante (`Benegnado`) acessa a plataforma (`http://localhost:8000/`) e faz login.
2. No Painel Principal (`/dashboard/`), o sistema lista todos os eventos em que ele foi inscrito pela equipe administrativa.
3. Se um formulário de impacto estiver vinculado ao evento e ainda não tiver sido respondido, um botão chamado **"Responder Formulário"** estará visível em destaque.

## 2. Preenchimento do Formulário
1. Ao clicar no botão, a tela do formulário será aberta (`/impact/respond/<id>/`).
2. O participante verá as instruções com a escala Likert (1 a 5), onde 1 significa insatisfação total e 5 significa aprovação total.
3. **Perguntas Objetivas**: Estarão listadas as 10 perguntas padrão englobando as dimensões de:
   - Conscientização
   - Educação
   - Ação
4. O participante deve obrigatoriamente marcar uma opção (de 1 a 5) em cada pergunta.
5. **Perguntas Abertas (Opcionais)**: No fim do formulário, há campos de texto livre para preenchimento qualitativo.

## 3. Submissão e Regra de Segurança
1. Ao final do formulário, o usuário clica em **"Enviar Respostas"**.
2. O sistema grava as informações no banco de dados, registrando carimbo de tempo.
3. A página de Sucesso será exibida.
4. **Proteção Anti-Duplicidade**: O sistema não permite que o mesmo participante responda o mesmo formulário duas vezes. O botão de resposta no painel será substituído por "✔ Formulário de Impacto Respondido". Se o usuário tentar acessar a URL do formulário diretamente, o sistema redirecionará informando que a resposta já foi processada.
