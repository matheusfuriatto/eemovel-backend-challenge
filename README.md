
# E-emovel: API de Logística e Processamento Geoespacial

Este projeto consiste em uma API RESTful especializada em operações logísticas, integrando processamento de dados geográficos, otimização de rotas e visualização de mapas. A solução utiliza uma arquitetura conteinerizada para garantir a consistência entre os ambientes de desenvolvimento e produção.

## Stack Tecnológica e Decisões de Arquitetura

A aplicação foi estruturada utilizando o padrão Application Factory do Flask, facilitando a escalabilidade e a implementação de testes de integração.

* **Backend:** Python 3.10 com Flask e Flask-RESTx (Swagger/OpenAPI).
* **Banco de Dados:** PostgreSQL 15 com extensão PostGIS para persistência de objetos geográficos.
* **Camada de Dados:** SQLAlchemy com GeoAlchemy2 para manipulação de tipos `Geography` e execução de queries espaciais nativas.
* **Segurança:** Autenticação stateless via JWT (Flask-JWT-Extended) e hashing de credenciais com Bcrypt.
* **GIS Server:** GeoServer para a publicação de camadas via protocolos OGC (WMS/WFS).
* **Infraestrutura:** Docker e Docker Compose para orquestração de serviços.

## Procedimentos de Inicialização

### Configuração de Ambiente

### Deploy do Ambiente

A orquestração via Docker Compose automatiza a subida do banco de dados, da API e do servidor de mapas.

```bash
docker-compose up --build

```

### Provisionamento Automático

O serviço `geoserver-setup` atua como um script de bootstrap que realiza as seguintes operações assim que os serviços atingem o estado de *healthy*:

1. Criação de Workspace e Datastore no GeoServer apontando para o PostGIS.
2. Publicação da camada de itens baseada em SQL Views.
3. Carga inicial de dados: o sistema é populado automaticamente com 10 coordenadas estratégicas de Cascavel, PR, para validação imediata da lógica de roteamento.

## Endpoints e Visualização

* **API Documentation:** Disponível na raiz do serviço (`http://localhost:5000/`), provendo interface Swagger para testes de contrato.
* **GIS Viewer:** Um cliente Leaflet está disponível em `http://localhost:5000/static/mapa.html`, consumindo dados via WFS diretamente do GeoServer.

### Autenticação para Testes

Para operações de escrita e otimização, utilize as credenciais pré-carregadas:

* **Usuário:** `teste@eemovel.com`
* **Senha:** `123`

## Lógica de Otimização de Roteiro

O endpoint `/items/optimize` implementa uma solução para o Problema de Roteamento de Veículos (VRP) utilizando a heurística do vizinho mais próximo (*Nearest Neighbor*).

O algoritmo processa a matriz de distâncias geográficas para agrupar pontos de entrega conforme a capacidade nominal do veículo informada no parâmetro `capacity`. O critério de agrupamento prioriza a minimização da distância euclidiana entre os pontos de uma mesma viagem, reduzindo o custo operacional de deslocamento.

## Validação e Qualidade de Código (Testes)

A suíte de testes de integração valida o fluxo completo, desde a autenticação até o cálculo de proximidade geográfica no banco de dados. Os testes são executados contra o banco de dados real para garantir a compatibilidade com as funções espaciais do PostGIS.

Para executar os testes de integração e validar o agrupamento de pontos em Cascavel:

```bash
docker-compose exec web pytest /app/tests/test_api.py -s

```
