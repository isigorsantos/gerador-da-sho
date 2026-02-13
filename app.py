from flask import Flask, render_template, request
import time
import hashlib
import requests
import json
from urllib.parse import urlparse

app = Flask(__name__)

# --- CONFIGURAÇÕES ---
MODO_MANUTENCAO = False 

# --- SEUS DADOS DA API ---
PARTNER_ID = 18322310004
PARTNER_KEY = "UIODYHCTHG2UZJLKOEP5ZINNEFRB3KHP"

def expandir_e_limpar(url_usuario):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url_usuario, allow_redirects=True, timeout=10, headers=headers)
        url_final = response.url
        if "shopee.com.br" in url_final:
            parsed = urlparse(url_final)
            return f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        return url_final
    except:
        return url_usuario

def converter_shopee(url_original):
    try:
        url_limpa = expandir_e_limpar(url_original)
        timestamp = int(time.time())
        url_api = "https://open-api.affiliate.shopee.com.br/graphql"
        payload = {"query": "mutation { generateShortLink(input: { originUrl: \"%s\" }) { shortLink } }" % url_limpa}
        payload_str = json.dumps(payload, separators=(',', ':'))
        base_string = str(PARTNER_ID) + str(timestamp) + payload_str + PARTNER_KEY
        signature = hashlib.sha256(base_string.encode('utf-8')).hexdigest()
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'SHA256 Credential={PARTNER_ID}, Timestamp={timestamp}, Signature={signature}'
        }
        response = requests.post(url_api, headers=headers, data=payload_str)
        dados = response.json()
        if "data" in dados and dados["data"] and dados["data"]["generateShortLink"]:
            return dados["data"]["generateShortLink"]["shortLink"]
        return None
    except:
        return None

@app.route('/', methods=['GET', 'POST'])
def index():
    if MODO_MANUTENCAO:
        return render_template('manutencao.html')
    
    link_final = None
    erro = None
    if request.method == 'POST':
        url_input = request.form.get('link_usuario', '').strip()
        if url_input:
            resultado = converter_shopee(url_input)
            if resultado and resultado.startswith("http"):
                # LIMPEZA DO LINK: Remove o ?lp=aff
                link_final = resultado.split('?')[0]
            else:
                erro = "Erro ao converter link."
                
    return render_template('index.html', link_novo=link_final, erro=erro)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
