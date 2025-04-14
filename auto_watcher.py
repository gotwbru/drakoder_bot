import json
import time
import mysql.connector
from datetime import datetime
import os

# Configuração do banco de dados
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'cpd2025',
    'database': 'pedidos_whatsapp'
}

# Caminho do arquivo JSON
ARQUIVO_JSON = 'mensagens.json'

# Intervalo entre checagens (em segundos)
INTERVALO = 5

def conectar():
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except mysql.connector.Error as err:
        print(f"❌ Erro de conexão com o banco: {err}")
        return None

def limpar_texto(valor):
    if isinstance(valor, str):
        return valor.replace('\xa0', ' ').replace('\u200b', '').strip()
    return valor

def normalizar_fornecedor_na_loja(valor):
    if not isinstance(valor, str):
        return valor
    valor = valor.replace('\xa0', ' ').replace('\u200b', '').strip().lower()
    if valor.startswith('sim'):
        return 'Sim'
    elif valor.startswith('não') or valor.startswith('nao'):
        return 'Não'
    return ''

def processar_mensagens():
    if not os.path.exists(ARQUIVO_JSON):
        print("⚠️ Arquivo mensagens.json não encontrado.")
        return

    with open(ARQUIVO_JSON, 'r', encoding='utf-8') as f:
        try:
            mensagens = json.load(f)
        except json.JSONDecodeError:
            print("❌ Erro ao ler JSON. Aguarde novo ciclo...")
            return

    if not mensagens:
        return

    conn = conectar()
    if conn is None:
        return

    cursor = conn.cursor()

    for item in mensagens:
        # Verifica e converte string JSON para dict
        if isinstance(item, str):
            try:
                item = json.loads(item)
            except json.JSONDecodeError:
                print(f"❌ Mensagem inválida (não é JSON): {item}")
                continue

        if not isinstance(item, dict):
            print(f"⚠️ Item ignorado (não é dicionário): {item}")
            continue

        tipo = item.get('tipo')
        dados = item.get('dados', {})

        # Limpa os campos
        dados = {k: limpar_texto(v) for k, v in dados.items()}
        dados['fornecedor_na_loja'] = normalizar_fornecedor_na_loja(dados.get('fornecedor_na_loja', ''))

        if tipo == 'solicitacao':
            data_solicitacao = dados.get('data_solicitacao')
            if data_solicitacao:
                try:
                    data_solicitacao = datetime.strptime(data_solicitacao, "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    data_solicitacao = datetime.now()
            else:
                data_solicitacao = datetime.now()

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
                data_solicitacao
            )
            try:
                cursor.execute(sql, valores)
                print(f"✅ Solicitação inserida: NF {dados.get('nota_fiscal')}")
            except Exception as e:
                print(f"❌ Erro ao inserir solicitação: {e}")

        elif tipo == 'resposta':
            try:
                cursor.execute("""
                    SELECT id FROM solicitacoes
                    WHERE nota_fiscal = %s
                    ORDER BY data_solicitacao DESC LIMIT 1
                """, (dados.get('nota_fiscal'),))
                resultado = cursor.fetchone()
                solicitacao_id = resultado[0] if resultado else None

                data_resposta = dados.get('data_resposta')
                if data_resposta:
                    try:
                        data_resposta = datetime.strptime(data_resposta, "%Y-%m-%d %H:%M:%S")
                    except ValueError:
                        data_resposta = datetime.now()
                else:
                    data_resposta = datetime.now()

                sql = """
                    INSERT INTO respostas (
                        nota_fiscal, status, data_resposta, solicitacao_id, respondido_por
                    ) VALUES (%s, %s, %s, %s, %s)
                """
                valores = (
                    dados.get('nota_fiscal', ''),
                    dados.get('status', ''),
                    data_resposta,
                    solicitacao_id,
                    dados.get('respondido_por', 'Não identificado')
                )
                cursor.execute(sql, valores)
                print(f"✅ Resposta inserida: NF {dados.get('nota_fiscal')} | Respondido por: {dados.get('respondido_por', 'Não identificado')}")
            except Exception as e:
                print(f"❌ Erro ao inserir resposta: {e}")

    conn.commit()
    cursor.close()
    conn.close()

    # Limpa o arquivo após processar
    with open(ARQUIVO_JSON, 'w', encoding='utf-8') as f:
        json.dump([], f, indent=2)
    print("🧹 mensagens.json limpo após processamento.\n")

if __name__ == '__main__':
    print("🔁 Iniciando monitoramento de mensagens.json...")
    while True:
        processar_mensagens()
        time.sleep(INTERVALO)
