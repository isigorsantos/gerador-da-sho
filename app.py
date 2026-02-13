from flask import Flask, render_template, request
import requests
import hashlib
import time
import json
from urllib.parse import urlparse

app = Flask(__name__)

# --- SEUS DADOS ---
PARTNER_ID = "18322310004"
PARTNER_KEY = "UIODYHCTHG2UZJLKOEP5ZINNEFRB3KHP"

# HISTÓRICO GLOBAL (Fica na memória do servidor)
# Nota: Na Vercel, isso pode resetar de vez em quando, mas funciona para quem estiver online
HISTORICO_GLOBAL = []

def converter_shopee(url_usuario):
    try:
        # 1. Limpa e expande o link
        r = requests.get(url_usuario, allow_redirects=True, timeout=5)
        url_real = r.url
        
        # 2. Gera o link de afiliado oficial
        timestamp = int(time.time())
        url_api = "https://open-api.affiliate.shopee.com.br/graphql"
        payload = {"query": 'mutation { gerarLinkCurto(entrada: { urlOrigem: "%s" }) { linkCurto } }' % url_real}
        payload_str = json.dumps(payload, separators=(',', ':'))
        assinatura = hashlib.sha256((PARTNER_ID + str(timestamp) + payload_str + PARTNER_KEY).encode('utf-8')).hexdigest()
        
        headers = {
            'Content-Type': 'application/json',
            'Autorização': f'Credencial SHA256={PARTNER_ID}, Timestamp={timestamp}, Assinatura={assinatura}'
        }
        
        res_api = requests.post(url_api, headers=headers, data=payload_str).json()
        link_final = res_api["data"]["gerarLinkCurto"]["linkCurto"]
        
        # 3. Adiciona ao histórico (Usamos a sua logo por padrão pois a Shopee bloqueia fotos externas)
        item = {"link": link_final, "titulo": "Produto Gerado Agora"}
        if item not in HISTORICO_GLOBAL:
            HISTORICO_GLOBAL.insert(0, item)
            if len(HISTORICO_GLOBAL) > 8: HISTORICO_GLOBAL.pop()
            
        return link_final
    except:
        return None

@app.route('/', methods=['GET', 'POST'])
def index():
    link_novo = None
    if request.method == 'POST':
        url = request.form.get('link_usuario', '').strip()
        if url:
            link_novo = converter_shopee(url)
            
    return render_template('index.html', link_novo=link_novo, historico=HISTORICO_GLOBAL)

if __name__ == '__main__':
    app.run(debug=True)
