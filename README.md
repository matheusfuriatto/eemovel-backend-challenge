
# E-emovel: API de Logística e Processamento Geoespacial

Este projeto consiste em uma API RESTful especializada em operações logísticas, integrando processamento de dados geográficos, otimização de rotas e visualização de mapas. A solução utiliza uma arquitetura conteinerizada para garantir a consistência entre os ambientes de desenvolvimento e produção.

## 📖 Documentação da API (Swagger)

A documentação interativa da API, contendo todos os modelos de dados, parâmetros de busca e requisitos de autenticação, está disponível em:
* **Swagger UI:** `http://localhost:5000/docs`

> **Nota de Autenticação:** Para testar os endpoints protegidos no Swagger, clique no botão **Authorize** no topo da página e insira o token no formato: `Bearer SEU_TOKEN_AQUI`.

## 🛠 Funcionalidades de Itens (`item_ns`)

O namespace de itens gerencia todas as operações geográficas e logísticas da aplicação:

1.  **Listagem Geral:** Retorna todos os itens cadastrados no banco de dados.
2.  **Busca Geoespacial por Raio:** No endpoint de listagem (`GET /items/`), é possível filtrar itens fornecendo os parâmetros `lat` (latitude), `lng` (longitude) e `radius` (raio em metros). A API utiliza a função `ST_DWithin` do PostGIS com cast para `Geography` para precisão métrica.
3.  **Cadastro de Pontos (CRUD):** Criação de novos itens enviando nome, descrição e coordenadas. O sistema persiste os dados usando o tipo `Geometry(POINT, 4326)`.
4.  **Atualização e Remoção:** Operações completas de `PUT` e `DELETE` para manutenção dos registros, protegidas por autenticação JWT.
5.  **Otimização de Roteiro (VRP):** Endpoint `/items/optimize` que implementa a heurística do **Vizinho Mais Próximo** para agrupar entregas baseando-se na proximidade geográfica e na capacidade de carga do veículo.



## Stack Tecnológica e Decisões de Arquitetura

A aplicação foi estruturada utilizando o padrão Application Factory do Flask, facilitando a escalabilidade e a implementação de testes.

* **Backend:** Python 3.10 com Flask e Flask-RESTx (Swagger/OpenAPI).
* **Banco de Dados:** PostgreSQL 15 com extensão PostGIS.
* **Camada de Dados:** SQLAlchemy com GeoAlchemy2 para manipulação de tipos geográficos.
* **Segurança:** Autenticação stateless via JWT (Flask-JWT-Extended) e hashing de senhas com Bcrypt.
* **GIS Server:** GeoServer para a publicação de camadas via protocolos OGC (WMS/WFS).
* **Infraestrutura:** Docker e Docker Compose.

## Procedimentos de Inicialização


### 1. Deploy do Ambiente via Docker

A orquestração automatiza a subida do banco de dados (com PostGIS), da API e do GeoServer:

```bash
docker-compose up --build

```

### 2. Provisionamento Automático (GeoServer)

O serviço `geoserver-setup` realiza o bootstrap automático assim que os serviços estão prontos:

* Criação de Workspace e Datastore.
* Publicação da camada de itens baseada em SQL Views.
* **Carga inicial de dados:** O sistema é populado automaticamente com coordenadas estratégicas de **Cascavel, PR**, para validação imediata.

## Endpoints e Visualização

* **API Documentation:** `http://localhost:5000/docs`
* **GIS Viewer:** Um cliente Leaflet disponível em `http://localhost:5000/static/mapa.html`, consumindo dados via WFS diretamente do GeoServer.

### Autenticação para Testes

* **Usuário:** `teste@eemovel.com`
* **Senha:** `123`

## Lógica de Otimização de Roteiro

O endpoint `/items/optimize` resolve o desafio de minimização de viagens. O algoritmo processa a matriz de distâncias geográficas para agrupar pontos de entrega conforme a capacidade nominal do veículo. O critério prioriza a redução da distância euclidiana entre os pontos de uma mesma viagem, reduzindo o custo operacional.

## Validação e Qualidade de Código (Testes)

A suíte de testes de integração valida o fluxo completo, desde a autenticação até o cálculo de proximidade no PostGIS. Para executar:

```bash
docker-compose exec web pytest /app/tests/test_api.py -s

```
