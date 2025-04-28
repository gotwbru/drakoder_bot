import json
import mysql.connector
from datetime import datetime
import os
import logging

# Configuração básica do logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Configuração da conexão com o MySQL
try:
    conexao = mysql.connector.connect(
        host='localhost',
        user='root',
        password='cpd2025',
        database='pedidos_whatsapp'
    )
    cursor = conexao.cursor()
except mysql.connector.Error as err:
    logging.error(f"❌ Erro ao conectar ao banco de dados: {err}")
    exit()

# Lê o arquivo mensagens.json
arquivo = 'mensagens.json'

if not os.path.exists(arquivo):
    logging.warning("⚠️ Arquivo mensagens.json não encontrado.")
    exit()

with open(arquivo, 'r', encoding='utf-8') as f:
    try:
        mensagens = json.load(f)
    except json.JSONDecodeError as err:
        logging.error(f"❌ Erro ao ler mensagens.json: {err}")
        exit()

if not mensagens:
    logging.info("📭 Nenhuma mensagem para inserir.")
else:
    for item in mensagens:
        tipo = item.get('tipo')
        dados = item.get('dados', {})

        try:
            if tipo == 'solicitacao':
                if not dados.get('nota_fiscal') or not dados.get('fornecedor'):
                    logging.warning(f"⚠️ Dados incompletos na solicitação: {dados}")
                    continue

                sql = """
                    INSERT INTO solicitacoes (
                        fornecedor, nota_fiscal, loja, motivo, comprador, fornecedor_na_loja, data_solicitacao
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                valores = (
                    dados.get('fornecedor', ''),
                    dados.get('nota_fiscal', ''),
                    dados.get('loja', ''),
                    dados.get('motivo', ''),
                    dados.get('comprador', ''),
                    dados.get('fornecedor_na_loja', ''),
                    datetime.now()
                )
                cursor.execute(sql, valores)
                logging.info(f"✅ Solicitação inserida: NF {dados.get('nota_fiscal')}")

            elif tipo == 'resposta':
                if not dados.get('nota_fiscal') or not dados.get('status'):
                    logging.warning(f"⚠️ Dados incompletos na resposta: {dados}")
                    continue

                cursor.execute(
                    "SELECT id FROM solicitacoes WHERE nota_fiscal = %s ORDER BY data_solicitacao DESC LIMIT 1",
                    (dados.get('nota_fiscal'),)
                )
                resultado = cursor.fetchone()
                solicitacao_id = resultado[0] if resultado else None

                if solicitacao_id is None:
                    logging.warning(f"⚠️ Solicitação correspondente não encontrada para NF {dados.get('nota_fiscal')}")
                    continue

                sql = """
                    INSERT INTO respostas (
                        nota_fiscal, status, data_resposta, solicitacao_id
                    ) VALUES (%s, %s, %s, %s)
                """
                valores = (
                    dados.get('nota_fiscal', ''),
                    dados.get('status', ''),
                    datetime.now(),
                    solicitacao_id
                )
                cursor.execute(sql, valores)
                logging.info(f"✅ Resposta inserida: NF {dados.get('nota_fiscal')}")

        except mysql.connector.Error as err:
            logging.error(f"❌ Erro ao inserir dados no banco: {err} - Dados: {dados}")
            continue

    # Salva no banco
    conexao.commit()

    # Limpa o conteúdo do arquivo após processar
    with open(arquivo, 'w', encoding='utf-8') as f:
        json.dump([], f, indent=2)

    logging.info("🧹 mensagens.json foi limpo após inserção.")

# Fecha conexões
cursor.close()
conexao.close()
