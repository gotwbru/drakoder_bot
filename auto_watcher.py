import json
import time
import mysql.connector
from mysql.connector import Error
from datetime import datetime
import os
from dotenv import load_dotenv
import logging

# Carrega as variáveis do .env
load_dotenv()

# Configuração básica do logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Configuração do banco de dados
DB_CONFIG = {
    'host': os.getenv("DB_HOST"),
    'port': int(os.getenv("DB_PORT")),
    'user': os.getenv("DB_USER"),
    'password': os.getenv("DB_PASSWORD"),
    'database': os.getenv("DB_NAME")
}

ARQUIVO_JSON = 'mensagens.json'
INTERVALO = 5

# Conecta ao banco
def conectar():
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except Error as err:
        logging.error(f"❌ Erro de conexão com o banco: {err}")
        return None

# Limpa texto e remove caracteres invisíveis
def limpar_texto(valor):
    if isinstance(valor, str):
        return valor.replace('\xa0', ' ') \
                    .replace('\u200b', '') \
                    .replace('\r', '') \
                    .replace('\t', '') \
                    .strip()
    return valor

# Padroniza o campo fornecedor_na_loja
def normalizar_fornecedor_na_loja(valor):
    if not isinstance(valor, str):
        return valor
    valor = valor.replace('\xa0', ' ').replace('\u200b', '').strip().casefold()
    if valor.startswith('sim'):
        return 'Sim'
    elif valor.startswith(('não', 'nao')):
        return 'Não'
    return ''

# Processa mensagens do JSON
def processar_mensagens():
    if not os.path.exists(ARQUIVO_JSON):
        logging.warning("⚠️ Arquivo mensagens.json não encontrado.")
        return

    with open(ARQUIVO_JSON, 'r', encoding='utf-8') as f:
        try:
            mensagens = json.load(f)
        except json.JSONDecodeError as e:
            logging.error(f"❌ Erro ao ler JSON: {e}")
            return

    if not mensagens:
        return

    conn = conectar()
    if conn is None:
        return

    cursor = conn.cursor()

    for item in mensagens:
        if isinstance(item, str):
            try:
                item = json.loads(item)
            except json.JSONDecodeError:
                logging.warning(f"❌ Mensagem inválida (não é JSON): {item}")
                continue

        if not isinstance(item, dict):
            logging.warning(f"⚠️ Item ignorado (não é dicionário): {item}")
            continue

        tipo = item.get('tipo')
        dados = item.get('dados', {})

        dados = {k: limpar_texto(v) for k, v in dados.items()}
        dados['fornecedor_na_loja'] = normalizar_fornecedor_na_loja(dados.get('fornecedor_na_loja', ''))

        try:
            if tipo == 'solicitacao':
                data_solicitacao = dados.get('data_solicitacao')
                try:
                    data_solicitacao = datetime.strptime(data_solicitacao, "%Y-%m-%d %H:%M:%S")
                except (ValueError, TypeError):
                    data_solicitacao = datetime.now()

                sql = '''
                    INSERT INTO solicitacoes (
                        fornecedor, nota_fiscal, loja, motivo, comprador, fornecedor_na_loja, data_solicitacao
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                '''
                valores = (
                    dados.get('fornecedor', ''), dados.get('nota_fiscal', ''), dados.get('loja', ''),
                    dados.get('motivo', ''), dados.get('comprador', ''), dados.get('fornecedor_na_loja', ''),
                    data_solicitacao
                )
                cursor.execute(sql, valores)
                logging.info(f"✅ Solicitação inserida: NF {dados.get('nota_fiscal')}")

            elif tipo == 'resposta':
                cursor.execute('''
                    SELECT id FROM solicitacoes
                    WHERE nota_fiscal = %s
                    ORDER BY data_solicitacao DESC LIMIT 1
                ''', (dados.get('nota_fiscal'),))
                resultado = cursor.fetchone()
                solicitacao_id = resultado[0] if resultado else None

                if solicitacao_id is None:
                    logging.warning(f"⚠️ Solicitação não encontrada para NF {dados.get('nota_fiscal')}")
                    continue

                data_resposta = dados.get('data_resposta')
                try:
                    data_resposta = datetime.strptime(data_resposta, "%Y-%m-%d %H:%M:%S")
                except (ValueError, TypeError):
                    data_resposta = datetime.now()

                sql = '''
                    INSERT INTO respostas (
                        nota_fiscal, status, data_resposta, solicitacao_id, respondido_por
                    ) VALUES (%s, %s, %s, %s, %s)
                '''
                valores = (
                    dados.get('nota_fiscal', ''), dados.get('status', ''), data_resposta,
                    solicitacao_id, dados.get('respondido_por', 'Não identificado')
                )
                cursor.execute(sql, valores)
                logging.info(f"✅ Resposta inserida: NF {dados.get('nota_fiscal')} por {dados.get('respondido_por', 'Não identificado')}")

        except Error as e:
            logging.error(f"❌ Erro ao inserir dados no banco: {e}")

    conn.commit()
    cursor.close()
    conn.close()

    with open(ARQUIVO_JSON, 'w', encoding='utf-8') as f:
        json.dump([], f, indent=2)
    logging.info("🧹 mensagens.json limpo após processamento.")

# Loop principal
if __name__ == '__main__':
    logging.info("🔁 Iniciando monitoramento de mensagens.json...")
    while True:
        processar_mensagens()
        time.sleep(INTERVALO)
