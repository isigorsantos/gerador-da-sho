from flask import Flask, render_template, request
import requests
import hashlib
import time
import json

app = Flask(__name__)

# SEUS DADOS OFICIAIS (O TOKEN QUE DEU CERTO)
PARTNER_ID = "18322310004"
PARTNER_KEY = "UIODYHCTHG2UZJLKOEP5ZINNEFRB3KHP"

def converter_shopee(url_usuario):
    try:
        # 1. Expandir o link para a URL real do produto
        r = requests.get(url_usuario, allow_redirects=True, timeout=5)
        url_real = r.url
        
        # 2. Gerar o link de afiliado via API Oficial
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
        return res_api["data"]["gerarLinkCurto"]["linkCurto"]
    except:
        return None

@app.route('/', methods=['GET', 'POST'])
def index():
    link_novo = None
    if request.method == 'POST':
        url = request.form.get('link_usuario', '').strip()
        if url:
            link_novo = converter_shopee(url)
    return render_template('index.html', link_novo=link_novo)

if __name__ == '__main__':
    app.run(debug=True)
