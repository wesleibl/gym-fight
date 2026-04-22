# gym-fight API

API REST para gerenciamento de academias de luta marcial. Controla alunos, instrutores, turmas e presenças, com autenticação JWT e controle de acesso por perfil.

## Tecnologias

- **Python 3.12**
- **FastAPI** — framework web
- **SQLModel** — ORM (SQLAlchemy + Pydantic)
- **SQLite** — banco de dados
- **pyjwt + pwdlib[argon2]** — autenticação JWT e hash de senhas
- **pytest + httpx** — testes

## Instalação

```bash
# Clone o repositório
git clone https://github.com/seu-usuario/gym-fight.git
cd gym-fight

# Crie e ative o ambiente virtual
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

# Instale as dependências
pip install -r requirements.txt

# Configure as variáveis de ambiente
cp .env.example .env
```

Edite o `.env`:

```env
DATABASE_URL=sqlite:///./gym-fight.db
SECRET_KEY=sua-chave-secreta-aqui
ACCESS_TOKEN_EXPIRE_MINUTES=15
```

## Executando

```bash
# Desenvolvimento (com hot reload)
fastapi dev app/main.py

# Produção
fastapi run app/main.py
```

A API estará disponível em `http://localhost:8000`.  
Documentação interativa: `http://localhost:8000/docs`

## Testes

```bash
# Todos os testes
pytest

# Arquivo específico
pytest tests/test_users.py

# Teste específico com output detalhado
pytest tests/test_users.py::test_create_user -v
```

## CI

O projeto usa **GitHub Actions** para rodar o `pytest` automaticamente em todo push e pull request. O workflow está em [.github/workflows/ci.yml](.github/workflows/ci.yml).

## Endpoints

### Autenticação

| Método | Rota | Descrição |
|--------|------|-----------|
| `POST` | `/auth/login` | Login, retorna JWT Bearer token |

### Usuários

| Método | Rota | Acesso | Descrição |
|--------|------|--------|-----------|
| `POST` | `/users/` | Público | Cadastrar novo aluno |
| `GET` | `/users/` | Instrutor | Listar todos os usuários |
| `GET` | `/users/{id}` | Autenticado | Ver usuário (instrutor vê qualquer um; aluno vê a si mesmo) |
| `PUT` | `/users/{id}` | Autenticado | Atualizar dados (nome, email, telefone) |
| `DELETE` | `/users/{id}` | Instrutor | Remover usuário |
| `PATCH` | `/users/{id}/level` | Instrutor | Alterar nível (`beginner` / `intermediate` / `advanced`) |
| `PATCH` | `/users/{id}/instructor` | Instrutor | Conceder ou revogar status de instrutor |
| `PATCH` | `/users/{id}/status` | Instrutor | Alterar status (`active` / `pastdue` / `blocked`) |
| `GET` | `/users/{id}/attendances` | Autenticado | Listar presenças (instrutor vê de qualquer um; aluno só as próprias) |

### Turmas (Schedules)

| Método | Rota | Acesso | Descrição |
|--------|------|--------|-----------|
| `POST` | `/schedules/` | Instrutor | Criar turma |
| `GET` | `/schedules/` | Autenticado | Listar todas as turmas |
| `GET` | `/schedules/available` | Autenticado | Listar turmas disponíveis para o perfil do usuário |
| `DELETE` | `/schedules/{id}` | Instrutor | Remover turma |

### Presenças (Attendences)

| Método | Rota | Acesso | Descrição |
|--------|------|--------|-----------|
| `POST` | `/attendences/` | Autenticado | Registrar presença |
| `GET` | `/attendences/` | Autenticado | Listar presenças (instrutor vê todas; aluno vê as suas) |
| `DELETE` | `/attendences/{id}` | Autenticado | Cancelar presença (instrutor cancela qualquer; aluno só a sua) |

## Autenticação

Todas as rotas protegidas exigem o header:

```
Authorization: Bearer <token>
```

O token é obtido via `POST /auth/login` e expira conforme `ACCESS_TOKEN_EXPIRE_MINUTES`.

## Tipos de turma

As turmas têm tipos que determinam quem pode se inscrever:

| Tipo | Disponível para |
|------|----------------|
| `common` | Todos |
| `athlete` | Usuários com `is_athletic = true` |
| `female` | Usuários com `gender = female` |
| `kids` | Usuários com menos de 12 anos |

## Modelos

### User
```
name, email, gender (male/female), birth_date, phone
level: beginner | intermediate | advanced
status: active | pastdue | blocked
is_instructor: bool
is_athletic: bool
```

### Schedule
```
day_of_week: monday | tuesday | wednesday | thursday | friday | saturday | sunday
time: HH:MM:SS
type: common | kids | female | athlete
```

### Attendence
```
user_id → User
schedule_id → Schedule
created_at
```
