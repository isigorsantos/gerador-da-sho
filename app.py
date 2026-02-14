from flask import Flask, render_template, request

app = Flask(__name__)

# Contadores iniciais (Eles resetam se o servidor da Vercel dormir no plano free)
stats = {
    'links': 1458,
    'visitas': 5291
}

@app.route('/', methods=['GET', 'POST'])
def index():
    # Conta visita real ao carregar a página
    stats['visitas'] += 1
    
    link_novo = None
    if request.method == 'POST':
        # Conta link gerado ao clicar no botão
        stats['links'] += 1
        link_usuario = request.form.get('link_usuario')
        
        # Simulação do link convertido (Aqui entra sua lógica real da Shopee)
        link_novo = "https://s.shopee.com.br/exemplo"

    return render_template('index.html', 
                           link_novo=link_novo, 
                           links_contagem=stats['links'], 
                           visitas_contagem=stats['visitas'])

if __name__ == '__main__':
    app.run(debug=True)
