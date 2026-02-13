from flask import Flask, render_template, request
import time
import hashlib
import requests
import json
from urllib.parse import urlparse

app = Flask(__name__)

# --- SEUS DADOS DA API ---
PARTNER_ID = 18322310004
PARTNER_KEY = "UIODYHCTHG2UZJLKOEP5ZINNEFRB3KHP"

def expandir_e_limpar(url_usuario):
    """ Descobre o link real e remove rastreadores pesados """
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        # 1. Segue redirecionamentos para chegar no link final da Shopee
        response = requests.get(url_usuario, allow_redirects=True, timeout=10, headers=headers)
        url_final = response.url
        
        # 2. LIMPEZA PROFUNDA: Se for um link de produto, ignora TUDO após o "?"
        # Isso remove utm_source, gads_t_sig e outras "sujeiras"
        if "shopee.com.br" in url_final:
            parsed = urlparse(url_final)
            url_limpa = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
            return url_limpa
        
        return url_final
    except Exception as e:
        print(f"Aviso na limpeza: {e}")
        return url_usuario

def converter_shopee(url_original):
    try:
        # PASSO 1: Limpeza antes de gerar a assinatura
        url_limpa = expandir_e_limpar(url_original)
        print(f"Processando link limpo: {url_limpa}")
        
        timestamp = int(time.time())
        url_api = "https://open-api.affiliate.shopee.com.br/graphql"
        
        payload = {
            "query": "mutation { generateShortLink(input: { originUrl: \"%s\" }) { shortLink } }" % url_limpa
        }
        # separators=(',', ':') é essencial para evitar o Erro 10020 (Assinatura Inválida)
        payload_str = json.dumps(payload, separators=(',', ':'))

        # PASSO 2: Assinatura Oficial (ID + TIMESTAMP + BODY + KEY)
        base_string = str(PARTNER_ID) + str(timestamp) + payload_str + PARTNER_KEY
        signature = hashlib.sha256(base_string.encode('utf-8')).hexdigest()

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'SHA256 Credential={PARTNER_ID}, Timestamp={timestamp}, Signature={signature}'
        }

        # PASSO 3: Envio e Tratamento do Resultado
        response = requests.post(url_api, headers=headers, data=payload_str)
        dados = response.json()

        if "data" in dados and dados["data"] and dados["data"]["generateShortLink"]:
            link_gerado = dados["data"]["generateShortLink"]["shortLink"]
            
            # REMOVE O ?LP=AFF AUTOMATICAMENTE SE A SHOPEE ENTREGAR
            if "?lp=aff" in link_gerado:
                link_gerado = link_gerado.replace("?lp=aff", "")
            
            return link_gerado
        
        if "errors" in dados:
            return f"Erro Shopee: {dados['errors'][0]['message']}"
            
        return "Erro na resposta da Shopee."

    except Exception as e:
        return f"Erro no sistema: {str(e)}"

@app.route('/', methods=['GET', 'POST'])
def index():
    link_final = None
    erro = None
    if request.method == 'POST':
        url_input = request.form.get('link_usuario', '').strip()
        if url_input:
            resultado = converter_shopee(url_input)
            if resultado and resultado.startswith("http"):
                link_final = resultado
            else:
                erro = resultado
    return render_template('index.html', link_novo=link_final, erro=erro)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)