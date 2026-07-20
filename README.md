# Instituto Economia ao Natural

## Rodar localmente (Windows)

1. Criar e ativar ambiente virtual:
   ```bash
   python -m venv venv
   .\venv\Scripts\activate
   ```

2. Instalar dependências:
   ```bash
   pip install -r requirements.txt
   ```

3. Criar arquivo .env com:
   ```
   DEBUG=True
   SECRET_KEY=chave_segura_local
   DB_NAME=...
   DB_USER=...
   DB_PASSWORD=...
   DB_HOST=localhost
   DB_PORT=5432
   ```

4. Rodar migrações:
   ```bash
   python manage.py migrate
   ```

5. Iniciar servidor:
   ```bash
   python manage.py runserver
   ```

## Produção (Resumo)

- Stack: Django 5, Gunicorn, Nginx, PostgreSQL.
- Deploy: VPS Hostinger + painel Coolify, com integração via GitHub.
- Subdomínio: institutoeconomiaaonatural.cocrias.com apontando para a VPS
