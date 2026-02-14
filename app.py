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

# Contador de ofertas (inicia em 0)
stats = {'links': 0}

def converter_link_shopee(link_original):
    try:
        timestamp = int(time.time())
        # Query exata do GraphQL da Shopee
        query = """
        mutation($originUrl: String!) {
          generateShortLink(originUrl: $originUrl) {
            shortLink
          }
        }
        """
        variables = {"originUrl": link_original}
        body = json.dumps({"query": query, "variables": variables})
        
        # A assinatura precisa ser ID + Timestamp + Body + Secret
        payload = APP_ID + str(timestamp) + body + APP_SECRET
        signature = hashlib.sha256(payload.encode('utf-8')).hexdigest()

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"SHA256 {APP_ID}:{timestamp}:{signature}"
        }

        response = requests.post(API_URL, headers=headers, data=body, timeout=15)
        res_json = response.json()
        
        # Retorna o link curto real da sua conta
        return res_json['data']['generateShortLink']['shortLink']
    except Exception as e:
        print(f"Erro na API Shopee: {e}")
        return None

@app.route('/', methods=['GET', 'POST'])
def index():
    link_novo = None
    if request.method == 'POST':
        link_usuario = request.form.get('link_usuario')
        if link_usuario:
            resultado = converter_link_shopee(link_usuario)
            if resultado:
                stats['links'] += 1
                link_novo = resultado
            else:
                # Mensagem que aparece na sua imagem quando a API falha
                link_novo = "Erro ao converter link. Verifique a URL."

    return render_template('index.html', 
                           link_novo=link_novo, 
                           links_contagem=stats['links'])

if __name__ == '__main__':
    app.run(debug=True)
