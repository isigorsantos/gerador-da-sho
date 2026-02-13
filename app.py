from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup
import hashlib
import time
import json

app = Flask(__name__)

# --- SEUS DADOS ---
PARTNER_ID = "18322310004"
PARTNER_KEY = "UIODYHCTHG2UZJLKOEP5ZINNEFRB3KHP"

# HISTÓRICO GLOBAL (Fica na memória do servidor para todos)
HISTORICO_GLOBAL = []

def buscar_metadados(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        res = requests.get(url, headers=headers, timeout=3) # Timeout curto para não travar
        soup = BeautifulSoup(res.text, 'html.parser')
        titulo = soup.find("meta", property="og:title")
        foto = soup.find("meta", property="og:image")
        return {
            "titulo": titulo["content"][:50] + "..." if titulo else "Produto em Oferta",
            "foto": foto["content"] if foto else "/static/logo.png"
        }
    except:
        return {"titulo": "Produto em Oferta", "foto": "/static/logo.png"}

def converter_shopee(url_usuario):
    try:
        # Expande o link
        r = requests.get(url_usuario, allow_redirects=True, timeout=5)
        url_real = r.url
        
        # API Shopee
        timestamp = int(time.time())
        url_api = "https://open-api.affiliate.shopee.com.br/graphql"
        payload = {"query": 'mutation { gerarLinkCurto(entrada: { urlOrigem: "%s" }) { linkCurto } }' % url_real}
        payload_str = json.dumps(payload, separators=(',', ':'))
        assinatura = hashlib.sha256((PARTNER_ID + str(timestamp) + payload_str + PARTNER_KEY).encode('utf-8')).hexdigest()
        
        headers = {'Content-Type': 'application/json', 'Autorização': f'Credencial SHA256={PARTNER_ID}, Timestamp={timestamp}, Assinatura={assinatura}'}
        res_api = requests.post(url_api, headers=headers, data=payload_str).json()
        link_f = res_api["data"]["gerarLinkCurto"]["linkCurto"]
        
        # Pega info para o histórico global
        info = buscar_metadados(url_real)
        item = {"link": link_f, "titulo": info["titulo"], "foto": info["foto"]}
        
        if item not in HISTORICO_GLOBAL:
            HISTORICO_GLOBAL.insert(0, item)
            if len(HISTORICO_GLOBAL) > 10: HISTORICO_GLOBAL.pop()
            
        return link_f
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
