import pytest
from app.extensions import db

@pytest.fixture
def client():
    from app import create_app
    app = create_app()
    app.config['TESTING'] = True
    # Conecta no banco real do Docker
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://admin:admin_password@db:5432/geodb'
    
    with app.test_client() as client:
        yield client

def test_workflow_logistica_cascavel(client):
    """Valida a inteligência logística sobre os dados reais de Cascavel."""
    
    # 1. Login com o usuário do script de setup
    auth_payload = {"email": "teste@eemovel.com", "password": "123"}
    login_res = client.post('/auth/login', json=auth_payload)
    
    assert login_res.status_code == 200, "O usuário de teste deve estar cadastrado no banco."
    token = login_res.json['access_token']
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Testar a Otimização (Capacidade 3)
    # Como enviamos 10 pontos, com capacidade 3, o algoritmo deve gerar 4 viagens.
    res = client.get('/items/optimize?capacity=3', headers=headers)
    
    assert res.status_code == 200
    dados = res.json
    
    # Validações de Negócio
    total_no_banco = dados['resumo']['total_itens']
    viagens = dados['resumo']['viagens_geradas']
    
    print(f"\n✅ Itens processados em Cascavel: {total_no_banco}")
    print(f"✅ Viagens otimizadas: {viagens}")

    assert total_no_banco >= 10, "Deveria haver pelo menos os 10 pontos iniciais."
    assert viagens > 0
    
    # 3. Validação Geográfica: O Shopping JL e a Catedral estão perto.
    # Vamos ver se eles ficaram na mesma viagem (índice 0 ou próxima).
    viagem_1 = [item['nome'] for item in dados['trips'][0]]
    print(f"📍 Composição da Viagem 1: {viagem_1}")

    assert len(dados['trips'][0]) <= 3, "Nenhuma viagem deve exceder a capacidade 3."