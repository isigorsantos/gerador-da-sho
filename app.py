from flask import Flask, render_template, request, session
import os

app = Flask(__name__)
# Chave necessária para usar sessões (cookies)
app.secret_key = os.urandom(24)

# Contadores Reais (Iniciam em zero)
stats = {
    'links': 0,
    'visitas': 0
}

@app.route('/', methods=['GET', 'POST'])
def index():
    # LÓGICA DE VISITA REAL POR SESSÃO
    # Só aumenta o contador se o usuário ainda não tiver o "carimbo" da sessão
    if 'visitou' not in session:
        stats['visitas'] += 1
        session['visitou'] = True # Marca que ele já visitou
    
    link_novo = None
    if request.method == 'POST':
        # Aumenta o link gerado real apenas no clique do botão
        stats['links'] += 1
        link_usuario = request.form.get('link_usuario')
        
        # Coloque sua lógica real de conversão de links aqui
        link_novo = "https://s.shopee.com.br/exemplo_real"

    return render_template('index.html', 
                           link_novo=link_novo, 
                           links_contagem=stats['links'], 
                           visitas_contagem=stats['visitas'])

if __name__ == '__main__':
    app.run(debug=True)
