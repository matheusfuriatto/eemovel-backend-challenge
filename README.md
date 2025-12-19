# 🌍 Sistema de Logística Inteligente - Eemovel

Esta aplicação é uma plataforma de inteligência geográfica voltada para logística. Ela permite o cadastro de pontos de interesse, visualização em mapa interativo e a geração de rotas otimizadas baseadas em proximidade geográfica e capacidade de carga.

## 🛠️ Tecnologias e Requisitos Técnicos

Para atender aos requisitos do desafio, foram utilizadas:

* **Backend:** Flask com Flask-RESTx (Swagger).
* **Segurança:** Autenticação JWT e criptografia de senhas com **Bcrypt**.
* **Banco de Dados:** PostgreSQL 15 com extensão **PostGIS** para dados espaciais.
* **Servidor de Mapas:** GeoServer para renderização de camadas geográficas.
* **Arquitetura:** Injeção de configurações via variáveis de ambiente e arquivo `.env`.

---

## 🚀 Como Executar o Projeto

O projeto é totalmente conteinerizado. Siga os passos abaixo:

1. **Clone o repositório:**
```bash
git clone <url-do-repositorio>
cd eemovel-api

```


2. **Suba o ambiente com Docker:**
```bash
docker-compose up --build

```


3. **Aguarde a Automação:**
O container `eemovel-geoserver-setup` irá configurar automaticamente o GeoServer e popular o banco com **10 pontos turísticos de São Paulo**. Quando o log exibir `✅ Automação concluída!`, o sistema estará pronto.

---

## 🧪 Como Executar os Testes

A aplicação possui uma suíte de testes robusta que valida a segurança (Bcrypt/JWT) e a lógica de otimização logística. Para rodar os testes dentro do container:

```bash
docker-compose exec web sh -c "PYTHONPATH=. pytest -s tests/"

```

**O que os testes validam?**

* **Bcrypt:** Se a senha é criptografada corretamente no banco.
* **JWT:** Se as rotas protegidas bloqueiam usuários não autenticados.
* **Logística:** Se o algoritmo de "Vizinho Mais Próximo" agrupa corretamente pontos próximos (Ex: Catedral da Sé e Pátio do Colégio na mesma viagem).

---

## 📍 Acessando o Sistema

### 1. Documentação da API (Swagger)

Interface interativa para testar todos os endpoints:
👉 **URL:** [http://localhost:5000/doc]

### 2. Mapa Interativo

Visualização dos pontos de São Paulo cadastrados:
👉 **URL:** [http://localhost:5000/static/mapa.html]

### 3. Credenciais de Teste (Padrão)

Para testar os endpoints protegidos no Swagger:

* **Usuário:** `teste@eemovel.com`
* **Senha:** `123`

---

## 💡 Lógica de Otimização (Diferencial)

O endpoint `/items/optimize` implementa um algoritmo de **Clusterização Geográfica**. Ao definir uma `capacity`, o sistema busca o ponto mais próximo de cada origem, otimizando o deslocamento.

Exemplo prático com os dados inclusos:

* **Viagem 1:** Agrupa pontos do Centro (Sé, Pátio do Colégio).
* **Viagem 2:** Agrupa pontos da Zona Oeste (Beco do Batman, Instituto Butantan).

---

## 📂 Estrutura de Configuração

O projeto utiliza um arquivo `.env` para gerenciar senhas e URLs de conexão. O arquivo `utils/config.py` centraliza essas informações, seguindo as melhores práticas de arquitetura Flask (Application Factory).

---

