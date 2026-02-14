from flask import Flask, render_template, request

app = Flask(__name__)

# Contadores Reais (Iniciam em zero)
# Nota: Na Vercel (plano grátis), esses números resetam se o site ficar inativo por muito tempo.
stats = {
    'links': 0,
    'visitas': 0
}

@app.route('/', methods=['GET', 'POST'])
def index():
    # Aumenta 1 visita real APENAS quando a página é carregada ou atualizada
    stats['visitas'] += 1
    
    link_novo = None
    if request.method == 'POST':
        # Aumenta 1 link gerado APENAS quando o formulário é enviado
        stats['links'] += 1
        link_usuario = request.form.get('link_usuario')
        
        # Sua lógica de conversão aqui
        link_novo = "https://s.shopee.com.br/exemplo_real"

    return render_template('index.html', 
                           link_novo=link_novo, 
                           links_contagem=stats['links'], 
                           visitas_contagem=stats['visitas'])

if __name__ == '__main__':
    app.run(debug=True)
