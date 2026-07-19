# Manual 01: Autenticação e Cadastro (Benegnados)

Este manual descreve o passo a passo para um usuário final (participante) se cadastrar e acessar o sistema do Instituto Economia ao Natural.

## 1. Acesso à Plataforma
1. Abra o navegador e acesse a URL inicial: `http://localhost:8000/`.
2. Como não há sessão ativa, você visualizará a barra superior (Navbar) com as opções **Entrar** e **Cadastrar-se**.

## 2. Cadastro de Novo Participante (Benegnado)
1. Clique no botão **Cadastrar-se** na barra superior (ou acesse `http://localhost:8000/accounts/signup/`).
2. Preencha os dados do formulário:
   - **Nome de Usuário**: um identificador único (ex: `joao_silva`).
   - **E-mail**: seu endereço de e-mail válido.
   - **Senha e Confirmação de Senha**: senha segura.
   - **Nome e Sobrenome**: dados pessoais.
   - **Empresa, Cargo e Cidade**: informações de perfil profissional.
3. Clique no botão **Cadastrar**.
4. Em caso de sucesso, o sistema criará o usuário e o perfil `Benegnado` automaticamente e o redirecionará para o Painel do Participante.

## 3. Login no Sistema
1. Caso já possua conta, clique em **Entrar** na página inicial (ou acesse `http://localhost:8000/accounts/login/`).
2. Insira o **Nome de Usuário ou E-mail** e a **Senha**.
3. Clique em **Entrar**.
4. Você será redirecionado para o **Painel do Participante** (`/dashboard/`).

## 4. Logout (Sair)
1. Para encerrar a sessão, localize o botão **Sair** no canto superior direito.
2. Ao clicar, você será desconectado e retornado para a tela de Login.
