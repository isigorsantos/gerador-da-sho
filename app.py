from flask import Flask, render_template, request
import hashlib
import time
import json
import requests

app = Flask(__name__)

# Suas Credenciais Reais Blindadas
APP_ID = "18322310004"
APP_SECRET = "UIODYHCTHG2UZJLKOEP5ZINNEFRB3KHP"
API_URL = "https://open-api.affiliate.shopee.com.br/graphql"

def converter_link_shopee(link_original):
    try:
        timestamp = int(time.time())
        # Query GraphQL específica para a API da Shopee
        query = 'mutation { generateShortLink(originUrl: "' + link_original + '") { shortLink } }'
        body = json.dumps({"query": query})
        
        # Gerando a Assinatura (Signature) obrigatória
        payload = APP_ID + str(timestamp) + body + APP_SECRET
        signature = hashlib.sha256(payload.encode()).hexdigest()

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"SHA256 {APP_ID}:{timestamp}:{signature}"
        }

        response = requests.post(API_URL, headers=headers, data=body, timeout=10)
        res_json = response.json()
        
        # Extrai o link curto do retorno da API
        return res_json['data']['generateShortLink']['shortLink']
    except Exception as e:
        print(f"Erro na conversão: {e}")
        return None

@app.route('/', methods=['GET', 'POST'])
def index():
    link_novo = None
    if request.method == 'POST':
        link_usuario = request.form.get('link_usuario')
        if link_usuario:
            # Chama a função real de conversão usando sua API
            resultado = converter_link_shopee(link_usuario)
            if resultado:
                link_novo = resultado
            else:
                link_novo = "Erro: Verifique se o link é um produto válido da Shopee."

    return render_template('index.html', link_novo=link_novo)

if __name__ == '__main__':
    app.run(debug=True)
