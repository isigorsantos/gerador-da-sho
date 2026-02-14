from flask import Flask, render_template, request

app = Flask(__name__)

# Contadores Reais começando do ZERO
# ATENÇÃO: Na Vercel (plano grátis), esses números resetam se o site ficar sem acesso por um tempo.
stats = {
    'links': 0,
    'visitas': 0
}

@app.route('/', methods=['GET', 'POST'])
def index():
    # Toda vez que a página é acessada (GET ou POST), conta como 1 visita real
    stats['visitas'] += 1
    
    link_novo = None
    if request.method == 'POST':
        # Toda vez que o formulário é enviado, conta como 1 link gerado real
        stats['links'] += 1
        link_usuario = request.form.get('link_usuario')
        
        # Aqui você deve manter sua lógica real de conversão de links
        link_novo = "https://s.shopee.com.br/exemplo_real"

    return render_template('index.html', 
                           link_novo=link_novo, 
                           links_contagem=stats['links'], 
                           visitas_contagem=stats['visitas'])

if __name__ == '__main__':
    app.run(debug=True)
