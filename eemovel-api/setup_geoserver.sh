#!/bin/sh

# --- 1. CONFIGURAÇÃO DO GEOSERVER ---
echo "🚀 Iniciando configuração do GeoServer..."

# Habilitar JSONP (Necessário para o Leaflet ler os dados)
curl -u admin:geoserver -X PUT -H "Content-type: text/xml" \
  -d "<global><jsonpEnabled>true</jsonpEnabled></global>" \
  http://geoserver:8080/geoserver/rest/settings

# Criar Workspace
curl -u admin:geoserver -X POST -H "Content-type: text/xml" \
  -d "<workspace><name>logistica</name></workspace>" \
  http://geoserver:8080/geoserver/rest/workspaces

# Criar Store (PostGIS) - usando admin/admin_password do seu compose
curl -u admin:geoserver -X POST -H "Content-type: text/xml" \
  -d "<dataStore>
        <name>postgis_db</name>
        <connectionParameters>
          <host>db</host>
          <port>5432</port>
          <database>geodb</database>
          <user>admin</user>
          <passwd>admin_password</passwd>
          <dbtype>postgis</dbtype>
        </connectionParameters>
      </dataStore>" \
  http://geoserver:8080/geoserver/rest/workspaces/logistica/datastores

# Publicar a Camada (Baseado na tabela 'items')
curl -u admin:geoserver -X POST -H "Content-type: text/xml" \
  -d "<featureType><name>items</name><srs>EPSG:4326</srs></featureType>" \
  http://geoserver:8080/geoserver/rest/workspaces/logistica/datastores/postgis_db/featuretypes

# --- 2. AUTENTICAÇÃO E CADASTRO DE DADOS (API FLASK) ---
echo "🔐 Autenticando na API Flask..."

# Registrar o usuário (Caso ainda não exista)
curl -s -X POST http://web:5000/auth/register \
     -H "Content-Type: application/json" \
     -d '{"email": "teste@eemovel.com", "password": "123"}'

# Fazer login e extrair o token de forma robusta usando 'cut'
# O JSON esperado é {"access_token": "VALOR"}
RESPONSE=$(curl -s -X POST http://web:5000/auth/login \
     -H "Content-Type: application/json" \
     -d '{"email": "teste@eemovel.com", "password": "123"}')

# Extrai o valor que está entre a segunda e terceira aspa após access_token
TOKEN=$(echo $RESPONSE | cut -d '"' -f 4)

if [ -z "$TOKEN" ] || [ "$TOKEN" = "msg" ]; then
    echo "❌ Erro ao obter token. Resposta: $RESPONSE"
    exit 1
fi

echo "✅ Token obtido: ${TOKEN:0:10}..."

# Função para cadastrar pontos turísticos
post_item() {
    echo "Cadastrando: $1"
    curl -s -X POST http://web:5000/items/ \
         -H "Content-Type: application/json" \
         -H "Authorization: Bearer $TOKEN" \
         -d "{\"nome\": \"$1\", \"latitude\": $2, \"longitude\": $3, \"descricao\": \"$4\"}"
}

echo "📍 Enviando 10 pontos estratégicos de Cascavel, PR..."
post_item "Catedral Nossa Senhora Aparecida" -24.9554 -53.4552 "Centro"
post_item "Lago Municipal de Cascavel" -24.9610 -53.4350 "Região do Lago"
post_item "Prefeitura Municipal" -24.9605 -53.4475 "Centro"
post_item "Zoológico Municipal" -24.9625 -53.4250 "Região do Lago"
post_item "Calçadão da Avenida Brasil" -24.9545 -53.4590 "Centro"
post_item "Museu de Arte de Cascavel" -24.9520 -53.4520 "Centro"
post_item "Praça do Migrante" -24.9560 -53.4680 "Centro"
post_item "Teatro Municipal de Cascavel" -24.9515 -53.4485 "Centro"
post_item "Parque Vitória" -24.9450 -53.4380 "Country"
post_item "Expovel / Parque de Exposições" -24.9950 -53.4320 "Santos Dumont"

echo "✨ Tudo pronto! Verifique o mapa em http://localhost:5000/static/mapa.html"