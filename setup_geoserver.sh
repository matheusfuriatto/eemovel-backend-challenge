#!/bin/sh

echo "🚀 Iniciando configuração do GeoServer..."

# 1. Configurar GeoServer (comandos em linha única para evitar erro de aspas)
curl -u admin:geoserver -X PUT -H "Content-type: text/xml" -d "<global><jsonpEnabled>true</jsonpEnabled></global>" http://geoserver:8080/geoserver/rest/settings

curl -u admin:geoserver -X POST -H "Content-type: text/xml" -d "<workspace><name>logistica</name></workspace>" http://geoserver:8080/geoserver/rest/workspaces

curl -u admin:geoserver -X POST -H "Content-type: text/xml" -d "<dataStore><name>postgis_db</name><connectionParameters><host>db</host><port>5432</port><database>geodb</database><user>admin</user><passwd>admin_password</passwd><dbtype>postgis</dbtype></connectionParameters></dataStore>" http://geoserver:8080/geoserver/rest/workspaces/logistica/datastores

curl -u admin:geoserver -X POST -H "Content-type: text/xml" -d "<featureType><name>items</name><srs>EPSG:4326</srs></featureType>" http://geoserver:8080/geoserver/rest/workspaces/logistica/datastores/postgis_db/featuretypes

echo "🔐 Autenticando na API Flask..."

# 2. Registrar e Login
curl -s -X POST http://web:5000/auth/register -H "Content-Type: application/json" -d '{"email": "teste@eemovel.com", "password": "123"}'

RESPONSE=$(curl -s -X POST http://web:5000/auth/login -H "Content-Type: application/json" -d '{"email": "teste@eemovel.com", "password": "123"}')

# Extração do Token
TOKEN=$(echo $RESPONSE | cut -d '"' -f 4)

if [ -z "$TOKEN" ] || [ "$TOKEN" = "message" ]; then
    echo "❌ Erro no login. Resposta: $RESPONSE"
    exit 1
fi

echo "✅ Autenticado. Cadastrando pontos..."

# 3. Função de Cadastro
post_item() {
    curl -s -X POST http://web:5000/items/ -H "Content-Type: application/json" -H "Authorization: Bearer $TOKEN" -d "{\"nome\": \"$1\", \"latitude\": $2, \"longitude\": $3, \"descricao\": \"$4\"}"
    echo "📍 Item '$1' enviado."
}

post_item "Catedral" -24.9554 -53.4552 "Centro"
post_item "Lago Municipal" -24.9610 -53.4350 "Regiao do Lago"
post_item "Prefeitura" -24.9605 -53.4475 "Centro"
post_item "Zoologico" -24.9625 -53.4250 "Regiao do Lago"
post_item "Calcadao" -24.9545 -53.4590 "Centro"
post_item "Museu" -24.9520 -53.4520 "Centro"
post_item "Praca Migrante" -24.9560 -53.4680 "Centro"
post_item "Teatro" -24.9515 -53.4485 "Centro"
post_item "Parque Vitoria" -24.9450 -53.4380 "Country"
post_item "Expovel" -24.9950 -53.4320 "Santos Dumont"

echo "✨ Configuração concluída com sucesso!"