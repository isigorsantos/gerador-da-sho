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

# LISTA GLOBAL (Fica na memória do servidor para todos os usuários)
HISTORICO_GLOBAL = []

def capturar_detalhes(url):
    """ Tenta pegar a foto e o nome do produto sem travar o site """
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        res = requests.get(url, headers=headers, timeout=4)
        soup = BeautifulSoup(res.text, 'html.parser')
        titulo = soup.find("meta", property="og:title")
        foto = soup.find("meta", property="og:image")
        return {
            "titulo": titulo["content"][:60] + "..." if titulo else "Produto em Oferta",
            "foto": foto["content"] if foto else "/static/logo.png"
        }
    except:
        return {"titulo": "Produto Shopee 🧡", "foto": "/static/logo.png"}

def converter_shopee(url_usuario):
    try:
        # 1. Abre o link para pegar a URL real do produto
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
        
        # 3. Busca info para o histórico global
        info = capturar_detalhes(url_real)
        item = {"link": link_final, "titulo": info["titulo"], "foto": info["foto"]}
        
        # Adiciona no topo da lista global (limite de 10 itens)
        if item not in HISTORICO_GLOBAL:
            HISTORICO_GLOBAL.insert(0, item)
            if len(HISTORICO_GLOBAL) > 10: HISTORICO_GLOBAL.pop()
            
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
