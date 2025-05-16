from indice_kp import IndiceKP as kp 
from banco import meusqldb
from dados_dispo import dispositivo
from clima import climinha as clima
from sqlalchemy import create_engine, inspect, Column, Integer, String, Float, DateTime, MetaData, Table
from datetime import datetime

USER = 'root'
PASSWORD = 'MinhaSenha'
HOST = '127.0.0.1'
PORT = '3306'
DB_NAME = 'Banco_geral'
class main:
    def formatar_dados(self,dados):
        for item in dados:
            item['time_tag'] = datetime.fromisoformat(item['time_tag'])
        return dados

    def inserir_incice_kp(self):
        conn = meusqldb(USER, PASSWORD, HOST, PORT, DB_NAME)
        tabelas = conn.verifica_tabelas()
        
        if 'kp_indices' not in tabelas:
            colunas = [
                Column('id', Integer, primary_key=True, autoincrement=True),
                Column('time_tag', DateTime, nullable=False),
                Column('kp_index', Integer, nullable=False),
                Column('estimated_kp', Float, nullable=False),
                Column('kp', String(10), nullable=False)
            ]

            conn.criar_tabela_generica('kp_indices', colunas)
        else:
            print("Tabela 'kp_indices' já existe.")

        claskp = kp()
        dados = claskp.get_data()
        dados_banco = conn.selecionar_dados('kp_indices')
        dados_formatados = self.formatar_dados(dados)
        atualizados = []
        inseridor = []

        if dados_banco:
            time_tags_banco = {dado['time_tag'] for dado in dados_banco}
            
            for dado_formatado in dados_formatados:
                if dado_formatado['time_tag'] in time_tags_banco:
                    conn.atualizar_dados('kp_indices', {'time_tag': dado_formatado['time_tag']}, dado_formatado)
                    atualizados.append(dado_formatado)
                else:
                    conn.inserir_dados('kp_indices', [dado_formatado])
                    inseridor.append(dado_formatado)
        else:
            conn.inserir_dados('kp_indices', dados_formatados)

        print("Total registros atualizados:", len(atualizados))
        print("Total registros inseridos:", len(inseridor))
        print("Total registros:", len(dados_formatados))
        
    def inserir_dados_dispositivo(self):
        conn = meusqldb(USER, PASSWORD, HOST, PORT, DB_NAME)
        tabelas = conn.verifica_tabelas()
        dados_dispo = dispositivo()
        dados = dados_dispo.get_dados()
        
        if 'dispositivo' not in tabelas:
            colunas = [
                Column('id', Integer, primary_key=True, autoincrement=True),
                Column('ip', String(50)),
                Column('hostname', String(100)),
                Column('city', String(50)),
                Column('region', String(50)),
                Column('country', String(10)),
                Column('longitude', String(50)),
                Column('latitude', String(50)),
                Column('org', String(100)),
                Column('postal', String(20)),
                Column('timezone', String(50))
            ]

            conn.criar_tabela_generica('dispositivo', colunas)
            conn.inserir_dados('dispositivo', dados)
        else:
            print("Tabela 'dispositivo' já existe.")
            print("Atualizando dados do dispositivo...")
            filtro = {'id': 1}
            novos_dados = {
                'ip': dados['ip'],
                'hostname': dados['hostname'],
                'city': dados['city'],
                'region': dados['region'],
                'country': dados['country'],
                'longitude': dados['longitude'],
                'latitude': dados['latitude'],
                'org': dados['org'],
                'postal': dados['postal'],
                'timezone': dados['timezone']
            }
            conn.atualizar_dados('dispositivo', filtro, novos_dados)
            print("Dados do dispositivo atualizados com sucesso.")

        print("Dados de dispositivo inseridos com sucesso.")
    def inserir_clima(self):
        conn = meusqldb(USER, PASSWORD, HOST, PORT, DB_NAME)
        tabelas = conn.verifica_tabelas()
        
        if 'clima' not in tabelas:
            colunas = [
                Column('id', Integer, primary_key=True, autoincrement=True),
                Column('hora', DateTime, nullable=False),
                Column('temperatura', Float, nullable=False),
                Column('velocidade_vent', Float, nullable=False),
                Column('direcao_vent', Float, nullable=False),
                Column('latitude', Float, nullable=False),
                Column('longitude', Float, nullable=False)
            ]

            conn.criar_tabela_generica('clima', colunas)
        else:
            print("Tabela 'clima' já existe.")

        self.inserir_dados_dispositivo()
        banco_dispo = conn.selecionar_dados('dispositivo', {'id': 1})
        if not banco_dispo:
            print("Nenhum dado de dispositivo encontrado. Inserindo dados de dispositivo primeiro.")
        dados_clima = clima(banco_dispo[0]['longitude'], banco_dispo[0]['latitude'])
        dados = dados_clima.get_clima()
        temperatura = dados['current_weather']['temperature']
        velocidade_vent = dados['current_weather']['windspeed']
        direcao_vent = dados['current_weather']['winddirection']
        hora = datetime.fromisoformat(dados['current_weather']['time'])
        dados_formatados = {
            'hora': hora,
            'temperatura': temperatura,
            'velocidade_vent': velocidade_vent,
            'direcao_vent': direcao_vent,
            'latitude': banco_dispo[0]['latitude'],
            'longitude': banco_dispo[0]['longitude']
        }
        conn.inserir_dados('clima', dados_formatados)
        print("Dados climáticos inseridos com sucesso.")
    def main(self):
        conn = meusqldb(USER, PASSWORD, HOST, PORT, DB_NAME)
        existe = conn.criar_banco()
        if not existe:
            print("Erro ao criar o banco de dados.")
            return
        tabelas= conn.verifica_tabelas()

        print("Tabelas disponíveis:")
        for tabela in tabelas:
            print(tabela)

        self.inserir_incice_kp()
        self.inserir_clima()

if __name__ == "__main__":
    main_instance = main()
    main_instance.main()