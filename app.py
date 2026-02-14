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

stats = {'links': 0}

def converter_link_shopee(link_original):
    try:
        timestamp = int(time.time())
        query = """
        mutation ($link: String!) {
            generateShortLink(input: {originUrl: $link}) {
                shortLink
            }
        }
        """
        variables = {"link": link_original}
        body = json.dumps({"query": query, "variables": variables})
        
        # Gerando a Assinatura (Signature) exigida pela Shopee
        payload = APP_ID + str(timestamp) + body + APP_SECRET
        signature = hashlib.sha256(payload.encode()).hexdigest()

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"SHA256 {APP_ID}:{timestamp}:{signature}"
        }

        response = requests.post(API_URL, headers=headers, data=body)
        res_json = response.json()
        
        # Pega o link curto gerado
        link_curto = res_json['data']['generateShortLink']['shortLink']
        return link_curto
    except Exception as e:
        print(f"Erro na conversão: {e}")
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
                link_novo = "Erro ao converter link. Verifique a URL."

    return render_template('index.html', 
                           link_novo=link_novo, 
                           links_contagem=stats['links'])

if __name__ == '__main__':
    app.run(debug=True)
