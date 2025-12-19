import pytest
from app import create_app
from app.extensions import db

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    # Usando SQLite em memória para isolamento total dos testes
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:' 
    app.config['JWT_SECRET_KEY'] = 'test-secret'
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.drop_all()

def test_auth_workflow(client):
    """Valida o fluxo de autenticação: Registro -> Login -> Proteção JWT"""
    print("\n🔍 Iniciando testes de Autenticação...")

    # 1. Teste de Registro
    payload = {"email": "test@test.com", "password": "123"}
    reg_res = client.post('/auth/register', json=payload)
    assert reg_res.status_code == 201, f"❌ Erro no Registro: Esperado 201, obtido {reg_res.status_code}. Msg: {reg_res.data}"
    print("✅ Registro de usuário funcional (Bcrypt ok).")

    # 2. Teste de Login
    login_res = client.post('/auth/login', json=payload)
    assert login_res.status_code == 200, f"❌ Erro no Login: Credenciais válidas rejeitadas. Status: {login_res.status_code}"
    
    token = login_res.json.get("access_token")
    assert token is not None, "❌ Erro no Login: Access Token não retornado no JSON."
    print("✅ Login e geração de JWT funcionais.")

def test_logistics_optimization(client):
    """Valida a criação de pontos e a inteligência do algoritmo de otimização"""
    print("\n🔍 Iniciando testes de Logística...")

    # Preparação: Registro e Login
    payload = {"email": "logistica@test.com", "password": "123"}
    client.post('/auth/register', json=payload)
    login = client.post('/auth/login', json=payload)
    token = login.json['access_token']
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Teste de Cadastro de Itens Geográficos
    pontos = [
        {"nome": "MASP", "latitude": -23.5615, "longitude": -46.6559, "descricao": "Paulista"},
        {"nome": "Trianon", "latitude": -23.5621, "longitude": -46.6572, "descricao": "Paulista"},
        {"nome": "Ibirapuera", "latitude": -23.5874, "longitude": -46.6576, "descricao": "Parque"}
    ]

    for p in pontos:
        res = client.post('/items/', headers=headers, json=p)
        assert res.status_code == 201, f"❌ Falha ao cadastrar ponto {p['nome']}. Erro: {res.data}"
    
    print(f"✅ Cadastro de {len(pontos)} pontos geográficos validado.")

    # 2. Teste de Algoritmo de Otimização (Capacidade 2)
    # Com 3 pontos e capacidade 2, esperamos 2 viagens (2 pontos na primeira, 1 na segunda)
    opt_res = client.get('/items/optimize?capacity=2', headers=headers)
    
    assert opt_res.status_code == 200, "❌ Endpoint /optimize retornou erro."
    
    dados = opt_res.json
    resumo = dados.get('resumo', {})
    
    assert resumo.get('total_itens') == 3, f"❌ Contagem de itens errada. Esperado 3, obtido {resumo.get('total_itens')}"
    assert resumo.get('viagens_geradas') == 2, f"❌ Divisão de viagens errada. Esperado 2, obtido {resumo.get('viagens_geradas')}"
    
    # Validação da Proximidade: MASP e Trianon devem estar na mesma viagem (índice 0)
    viagem_1 = dados['trips'][0]
    nomes_viagem_1 = [item['nome'] for item in viagem_1]
    
    assert "MASP" in nomes_viagem_1 and "Trianon" in nomes_viagem_1, \
        f"❌ O algoritmo falhou em agrupar pontos vizinhos. Agrupamento obtido: {nomes_viagem_1}"
    
    print("✅ Algoritmo de vizinho mais próximo validado com sucesso (Clusterização geográfica).")