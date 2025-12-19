import time
from sqlalchemy import text
from sqlalchemy.exc import OperationalError
from app import create_app, db
from app.models import User, Item

app = create_app()

def initialize_database():
    """Tenta inicializar o banco de dados com retentativas para evitar erros de conexão"""
    with app.app_context():
        retries = 10
        while retries > 0:
            try:
                print(f"Tentando conectar ao banco... ({retries} tentativas restantes)")
                

                db.session.execute(text('CREATE EXTENSION IF NOT EXISTS postgis;'))
                db.session.commit()
                
                db.create_all()
                
                print("Banco de dados e extensões inicializados com sucesso!")
                return True
            except OperationalError as e:
                print(f"Banco ainda não está pronto. Erro: {e}")
                retries -= 1
                time.sleep(3)
        
        print("Erro: Não foi possível conectar ao banco após várias tentativas.")
        return False

if __name__ == '__main__':
    # Só inicia o servidor se o banco inicializar corretamente
    if initialize_database():

        app.run(host='0.0.0.0', port=5000, debug=True)
    else:
        exit(1)