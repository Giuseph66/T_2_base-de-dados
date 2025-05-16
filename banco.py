from sqlalchemy import create_engine, inspect, Column, Integer, String, Float, DateTime, MetaData, Table
from sqlalchemy.orm import sessionmaker
import pymysql
from datetime import datetime

class meusqldb:
    def __init__(self, user, password, host, port, db_name):
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.db_name = db_name
        self.DATABASE_URL = f'mysql+pymysql://{self.user}:{self.password}@{self.host}:{self.port}/{self.db_name}'

    def connect(self):
        try:
            conn = pymysql.connect(
                user=self.user,
                password=self.password,
                host=self.host,
                port=int(self.port),
                database=self.db_name
            )
            print("Conexão com o banco de dados estabelecida com sucesso.")
            return conn
        except pymysql.MySQLError as err:
            print(f"Erro ao conectar ao MySQL: {err}")
            exit(1)

    def criar_banco(self):
        try:
            conn = self.connect()
            cursor = conn.cursor()
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.db_name}")
            print(f"Banco de dados '{self.db_name}' verificado/criado com sucesso.")
            cursor.close()
            return True
        except pymysql.MySQLError as err:
            print(f"Erro ao criar/verificar o banco de dados: {err}")
            exit(1)
            return False

    def criar_tabela(self, engine):
        metadata = MetaData()
        tabela_kp = Table(
            'kp_indices', metadata,
            Column('id', Integer, primary_key=True, autoincrement=True),
            Column('time_tag', DateTime, nullable=False),
            Column('kp_index', Integer, nullable=False),
            Column('estimated_kp', Float, nullable=False),
            Column('kp', String(10), nullable=False)
        )
        metadata.create_all(engine)
        print("Tabela 'kp_indices' criada/verificada com sucesso.")
        return tabela_kp

    def criar_tabela_generica(self, nome_tabela, colunas):
        metadata = MetaData()
        tabela = Table(nome_tabela, metadata, *colunas)
        engine = self.cria_engine()
        metadata.create_all(engine)
        print(f"Tabela '{nome_tabela}' criada/verificada com sucesso.")
        return tabela

    def verifica_tabelas(self):
        inspector = inspect(self.cria_engine())
        tabelas = inspector.get_table_names()

        if tabelas:
            print("Tabelas existentes no banco de dados:")
            return tabelas
        else:
            print("Nenhuma tabela encontrada no banco de dados.")
            return []

    def cria_engine(self):
        return create_engine(self.DATABASE_URL, echo=False)

    def inserir_dados(self, nome_tabela, dados):
        engine = self.cria_engine()
        metadata = MetaData()
        tabela = Table(nome_tabela, metadata, autoload_with=engine)
        conn = self.connect()
        with engine.connect() as conn:
            conn.execute(tabela.insert(), dados)
            conn.commit()
            print(f"Dados inseridos com sucesso na tabela '{nome_tabela}'.")

    def atualizar_dados(self, nome_tabela, filtro, novos_dados):
        engine = self.cria_engine()
        metadata = MetaData()
        tabela = Table(nome_tabela, metadata, autoload_with=engine)

        with engine.connect() as conn:
            query = tabela.update().where(
                *(tabela.c[chave] == valor for chave, valor in filtro.items())
            ).values(**novos_dados)
            resultado = conn.execute(query)

    def selecionar_dados(self, nome_tabela, filtro=None):
        engine = self.cria_engine()
        metadata = MetaData()
        tabela = Table(nome_tabela, metadata, autoload_with=engine)

        with engine.connect() as conn:
            if filtro:
                query = tabela.select().where(
                    *(tabela.c[chave] == valor for chave, valor in filtro.items())
                )
            else:
                query = tabela.select()

            resultado = conn.execute(query).mappings()  
            registros = [dict(row) for row in resultado]
            return registros

