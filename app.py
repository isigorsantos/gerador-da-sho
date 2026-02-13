from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup
import hashlib
import time
import json
from urllib.parse import urlparse

app = Flask(__name__)

PARTNER_ID = "18322310004"
PARTNER_KEY = "UIODYHCTHG2UZJLKOEP5ZINNEFRB3KHP"

def buscar_info_basica(url):
    """ Tenta pegar foto e título, mas não trava se falhar """
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        res = requests.get(url, headers=headers, timeout=5)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        titulo = soup.find("meta", property="og:title")
        foto = soup.find("meta", property="og:image")
        
        return {
            "titulo": titulo["content"] if titulo else "Produto em Oferta",
            "foto": foto["content"] if foto else "/static/logo.png"
        }
    except:
        return {"titulo": "Produto em Oferta", "foto": "/static/logo.png"}

def converter_shopee(url_usuario):
    try:
        # 1. Expandir link curto se necessário
        headers = {'User-Agent': 'Mozilla/5.0'}
        r = requests.get(url_usuario, allow_redirects=True, timeout=5, headers=headers)
        url_real = r.url
        
        # 2. Gerar Link de Afiliado via API
        timestamp = int(time.time())
        url_api = "https://open-api.affiliate.shopee.com.br/graphql"
        payload = {"query": 'mutation { gerarLinkCurto(entrada: { urlOrigem: "%s" }) { linkCurto } }' % url_real}
        payload_str = json.dumps(payload, separators=(',', ':'))
        assinatura = hashlib.sha256((PARTNER_ID + str(timestamp) + payload_str + PARTNER_KEY).encode('utf-8')).hexdigest()
        
        cabecalhos = {
            'Content-Type': 'application/json',
            'Autorização': f'Credencial SHA256={PARTNER_ID}, Timestamp={timestamp}, Assinatura={assinatura}'
        }
        
        res_api = requests.post(url_api, headers=cabecalhos, data=payload_str).json()
        link_final = res_api["data"]["gerarLinkCurto"]["linkCurto"]

        # 3. Buscar info do produto (AQUI É O EXTRA)
        info = buscar_info_basica(url_real)

        return {"link": link_final, "titulo": info["titulo"], "foto": info["foto"]}
    except:
        return None

@app.route('/', methods=['GET', 'POST'])
def index():
    resultado = None
    if request.method == 'POST':
        link_original = request.form.get('link_usuario', '').strip()
        if link_original:
            resultado = converter_shopee(link_original)
    return render_template('index.html', res=resultado)

if __name__ == '__main__':
    app.run(debug=True)
