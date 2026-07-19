# Manual 07: Sistema de Rastreio e Agendamento de E-mails

Este manual explica o funcionamento dos bastidores do sistema de comunicações e lembretes integrados.

## 1. Lembretes Agendados (django-q2)
O sistema foi configurado para disparar um "Cron Job" periódico de verificação de formulários não respondidos.
1. Uma `Schedule` (Agenda) rodando na fila de mensageria do `django-q2` dispara a tarefa `process_scheduled_emails` automaticamente.
2. Este script iterará sobre todos os formulários de impacto ativos.
3. Ele varre a lista de participantes inscritos em cada evento e verifica, no banco de dados, se existe um registro de `ImpactResponse` para aquela pessoa.
4. Caso a pessoa **não** tenha respondido, o sistema envia um e-mail com o link de acesso ao formulário.
5. Se a pessoa já tiver respondido, o script pula o nome dela, evitando incômodos.

## 2. Logs de Disparo
Todo e-mail gerado pelo sistema é gravado na tabela `EmailLog`, armazenando:
- O destinatário.
- O assunto e conteúdo da mensagem.
- O status de disparo (Enviado/Falha).

## 3. Rastreamento (Pixel e Tracking)
O sistema incorpora tecnologias de rastreamento para medir engajamento nas comunicações:
- **Pixel de Abertura:** Uma imagem minúscula (`1x1` transparente) é embutida no corpo do e-mail. Quando o servidor de e-mail ou o cliente carrega as imagens, o endpoint `/communications/track/pixel/<uuid>/` é acessado, registrando o carimbo de tempo da abertura na tabela `EmailTracking`.
- **Link de Clique:** Os links no e-mail não levam o usuário diretamente para o formulário. Eles apontam para `/communications/track/click/<uuid>/`. O servidor anota o horário do clique no banco de dados e, milissegundos depois, redireciona o usuário para o destino verdadeiro.
