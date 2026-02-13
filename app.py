from flask import Flask, render_template, request
import time
import hashlib
import requests
import json
import re
from urllib.parse import urlparse

app = Flask(__name__)

MODO_MANUTENCAO = False 
ULTIMOS_PRODUTOS = [] 

PARTNER_ID = 18322310004
PARTNER_KEY = "UIODYHCTHG2UZJLKOEP5ZINNEFRB3KHP"

def obter_detalhes_reais(url):
    """Busca o nome e a foto real do produto de forma mais robusta"""
    try:
        # Cabeçalhos de 'Pessoa Real' para não ser bloqueado
        headers = {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Mobile/15E148 Safari/604.1',
            'Accept-Language': 'pt-BR,pt;q=0.9'
        }
        response = requests.get(url, headers=headers, timeout=15)
        html = response.text
        
        # Pega o título real
        titulo_match = re.search(r'"name":"(.*?)"', html) or re.search(r'<title>(.*?)</title>', html)
        titulo = titulo_match.group(1).split(' | ')[0] if titulo_match else "Oferta Cupons da Sho 🧡"
        
        # Pega a foto real (tenta o link de alta qualidade primeiro)
        imagem_match = re.search(r'https://cf.shopee.com.br/file/(.*?)_tn', html) or re.search(r'https://cf.shopee.com.br/file/(.*?)"', html)
        imagem = imagem_match.group(0).replace('"', '') if imagem_match else "https://cf.shopee.com.br/file/857e2333f283597f8059080b06b02005"
        
        return titulo[:60] + "...", imagem
    except:
        return "Produto Verificado 🧡", "https://cf.shopee.com.br/file/857e2333f283597f8059080b06b02005"

def expandir_e_limpar(url_usuario):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url_usuario, allow_redirects=True, timeout=10, headers=headers)
        return response.url
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
            return dados["data"]["generateShortLink"]["shortLink"], url_limpa
        return None, None
    except:
        return None, None

@app.route('/', methods=['GET', 'POST'])
def index():
    if MODO_MANUTENCAO:
        return render_template('manutencao.html')
    
    link_final = None
    erro = None
    if request.method == 'POST':
        url_input = request.form.get('link_usuario', '').strip()
        if url_input:
            resultado_link, url_real = converter_shopee(url_input)
            if resultado_link and resultado_link.startswith("http"):
                # LIMPEZA TOTAL: Corta o ?lp=aff
                link_final = resultado_link.split('?')[0]
                
                # PEGA OS DADOS REAIS
                titulo_real, foto_real = obter_detalhes_reais(url_real)
                
                novo_item = {'link': link_final, 'titulo': titulo_real, 'imagem': foto_real}
                
                if not any(d['link'] == link_final for d in ULTIMOS_PRODUTOS):
                    ULTIMOS_PRODUTOS.insert(0, novo_item)
                if len(ULTIMOS_PRODUTOS) > 5:
                    ULTIMOS_PRODUTOS.pop()
            else:
                erro = "Link inválido ou não suportado."
                
    return render_template('index.html', link_novo=link_final, erro=erro, ranking=ULTIMOS_PRODUTOS)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
