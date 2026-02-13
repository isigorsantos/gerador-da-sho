from flask import Flask, render_template, request
import time
import hashlib
import requests
import json
import re
from urllib.parse import urlparse

app = Flask(__name__)

# --- CONFIGURAÇÕES ---
MODO_MANUTENCAO = False 
ULTIMOS_PRODUTOS = [] # Memória dos últimos 5 links

# --- SEUS DADOS DA API ---
PARTNER_ID = 18322310004
PARTNER_KEY = "UIODYHCTHG2UZJLKOEP5ZINNEFRB3KHP"

def obter_detalhes_reais(url):
    """Função que busca o título e a imagem real do produto na Shopee"""
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(url, headers=headers, timeout=10)
        html = response.text
        
        # Busca o título (og:title)
        titulo_match = re.search(r'<meta property="og:title" content="(.*?)"', html)
        titulo = titulo_match.group(1) if titulo_match else "Produto Shopee"
        
        # Busca a imagem (og:image)
        imagem_match = re.search(r'<meta property="og:image" content="(.*?)"', html)
        imagem = imagem_match.group(1) if imagem_match else "https://cf.shopee.com.br/file/857e2333f283597f8059080b06b02005"
        
        return titulo, imagem
    except:
        return "Produto Verificado 🧡", "https://cf.shopee.com.br/file/857e2333f283597f8059080b06b02005"

def expandir_e_limpar(url_usuario):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url_usuario, allow_redirects=True, timeout=10, headers=headers)
        url_final = response.url
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
                # LIMPEZA DO LINK: Remove o ?lp=aff
                link_final = resultado_link.split('?')[0]
                
                # BUSCA OS DETALHES REAIS (Foto e Nome)
                titulo_real, foto_real = obter_detalhes_reais(url_real)
                
                # ADICIONA AO RANKING
                novo_item = {
                    'link': link_final,
                    'titulo': titulo_real, 
                    'imagem': foto_real
                }
                
                # Verifica se o link já está na lista para não repetir
                if not any(d['link'] == link_final for d in ULTIMOS_PRODUTOS):
                    ULTIMOS_PRODUTOS.insert(0, novo_item)
                
                if len(ULTIMOS_PRODUTOS) > 5:
                    ULTIMOS_PRODUTOS.pop()
            else:
                erro = "Não conseguimos converter este link. Tente outro!"
                
    return render_template('index.html', link_novo=link_final, erro=erro, ranking=ULTIMOS_PRODUTOS)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
