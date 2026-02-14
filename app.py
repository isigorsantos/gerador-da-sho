from flask import Flask, render_template, request

app = Flask(__name__)

# Contador de Links Gerados (Inicia em zero)
# Nota: Na Vercel (plano grátis), esse número reseta se o site ficar inativo.
stats = {
    'links': 0
}

@app.route('/', methods=['GET', 'POST'])
def index():
    link_novo = None
    
    if request.method == 'POST':
        # Aumenta o contador apenas quando o link é gerado com sucesso
        stats['links'] += 1
        link_usuario = request.form.get('link_usuario')
        
        # Mantenha aqui a sua lógica real de conversão da Shopee
        link_novo = "https://s.shopee.com.br/exemplo_real"

    return render_template('index.html', 
                           link_novo=link_novo, 
                           links_contagem=stats['links'])

if __name__ == '__main__':
    app.run(debug=True)
