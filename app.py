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

def buscar_metadados(url):
    """ Tenta capturar a foto e o título real do produto """
    try:
        # Headers mais completos para parecer um celular real acessando
        headers = {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
            'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7'
        }
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # Tenta pegar das tags OG (Open Graph) que a Shopee usa
        titulo = soup.find("meta", property="og:title")
        foto = soup.find("meta", property="og:image")
        
        # Se não achar na primeira, tenta na tag de Twitter Card
        if not titulo: titulo = soup.find("meta", name="twitter:title")
        if not foto: foto = soup.find("meta", name="twitter:image")

        return {
            "titulo": titulo["content"] if titulo else "Produto Shopee",
            "foto": foto["content"] if foto else "/static/logo.png"
        }
    except:
        return {"titulo": "Produto em Oferta", "foto": "/static/logo.png"}

def expandir_e_limpar(url_usuario):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        resposta = requests.get(url_usuario, allow_redirects=True, timeout=10, headers=headers)
        url_final = resposta.url
        analisado = urlparse(url_final)
        return f"{analisado.scheme}://{analisado.netloc}{analisado.path}"
    except:
        return url_usuario

def converter_shopee(url_original):
    try:
        url_limpa = expandir_e_limpar(url_original)
        # PEGA AS INFOS REAIS AQUI
        dados_produto = buscar_metadados(url_limpa)
        
        timestamp = int(time.time())
        url_api = "https://open-api.affiliate.shopee.com.br/graphql"
        payload = {
            "query": 'mutation { gerarLinkCurto(entrada: { urlOrigem: "%s" }) { linkCurto } }' % url_limpa
        }
        payload_str = json.dumps(payload, separators=(',', ':'))
        assinatura = hashlib.sha256((PARTNER_ID + str(timestamp) + payload_str + PARTNER_KEY).encode('utf-8')).hexdigest()
        
        cabecalhos = {
            'Content-Type': 'application/json',
            'Autorização': f'Credencial SHA256={PARTNER_ID}, Timestamp={timestamp}, Assinatura={assinatura}'
        }
        
        res = requests.post(url_api, headers=cabecalhos, data=payload_str).json()
        link_curto = res["data"]["gerarLinkCurto"]["linkCurto"]
        
        return {
            "link": link_curto,
            "titulo": dados_produto["titulo"],
            "foto": dados_produto["foto"]
        }
    except:
        return None

@app.route('/', methods=['GET', 'POST'])
def index():
    resultado = None
    if request.method == 'POST':
        url = request.form.get('link_usuario', '').strip()
        if url:
            resultado = converter_shopee(url)
            
    return render_template('index.html', res=resultado)

if __name__ == '__main__':
    app.run(debug=True)
