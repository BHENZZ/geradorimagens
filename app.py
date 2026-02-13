#!/usr/bin/env python3
"""
Aplicação Web Flask para Gerador de Imagens de Produtos
Com upload de imagem de referência e template
"""

from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
import google.generativeai as genai
import os
import io
import base64
from datetime import datetime
from PIL import Image
import json

app = Flask(__name__)
CORS(app)

# Configurar API Key
API_KEY = os.getenv("GOOGLE_API_KEY", "AIzaSyCU8tdR0ikIEu9qWZftd6LCPjk5jBn-iLQ")
genai.configure(api_key=API_KEY)

# Criar pastas
OUTPUT_FOLDER = "static/imagens_geradas"
UPLOAD_FOLDER = "static/uploads"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    """Página principal"""
    return render_template('index.html')

@app.route('/gerar', methods=['POST'])
def gerar_imagem():
    """Endpoint para gerar imagem com produto"""
    try:
        # Pegar dados do formulário
        ficha_tecnica = request.form.get('ficha_tecnica', '')
        num_imagens = int(request.form.get('num_imagens', 1))
        aspect_ratio = request.form.get('aspect_ratio', '1:1')
        
        # Pegar arquivos
        imagem_produto = request.files.get('imagem_produto')
        template = request.files.get('template')
        
        if not ficha_tecnica:
            return jsonify({'erro': 'Ficha técnica é obrigatória'}), 400
        
        if not imagem_produto:
            return jsonify({'erro': 'Imagem do produto é obrigatória'}), 400
        
        # Salvar imagens temporariamente
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        produto_filename = f"produto_{timestamp}.png"
        produto_path = os.path.join(UPLOAD_FOLDER, produto_filename)
        imagem_produto.save(produto_path)
        
        template_path = None
        if template:
            template_filename = f"template_{timestamp}.png"
            template_path = os.path.join(UPLOAD_FOLDER, template_filename)
            template.save(template_path)
        
        # Criar prompt padrão otimizado para marketplaces
        if template_path:
            prompt = f"""Gere imagens desse produto em diferentes ângulos adicionando textos sobre a ficha técnica utilizando ícones e textos rápidos para maximizar conversão em marketplaces.

FICHA TÉCNICA:
{ficha_tecnica}

INSTRUÇÕES PARA ALTA CONVERSÃO EM MARKETPLACES:
1. Mostre o produto em ângulos diferentes e estratégicos
2. Use ÍCONES visuais para destacar características (✓, ⭐, 🔒, etc)
3. Textos CURTOS e DIRETOS que chamem atenção
4. Destaque BENEFÍCIOS principais com fontes grandes e legíveis
5. Use cores CONTRASTANTES para textos importantes
6. Adicione BADGES/SELOS de qualidade se aplicável
7. Mantenha fundo LIMPO para destaque do produto
8. Siga o estilo do template fornecido
9. Foco em CONVERSÃO e VENDAS
"""
        else:
            prompt = f"""Gere imagens desse produto em diferentes ângulos adicionando textos sobre a ficha técnica utilizando ícones e textos rápidos para maximizar conversão em marketplaces.

FICHA TÉCNICA:
{ficha_tecnica}

INSTRUÇÕES PARA ALTA CONVERSÃO EM MARKETPLACES:
1. Mostre o produto em 3-4 ângulos diferentes (frente, lateral, detalhe, uso)
2. Use ÍCONES visuais para cada benefício (✓, ⭐, 🔒, 💧, 🔥, etc)
3. Textos CURTOS e IMPACTANTES (máximo 3-5 palavras por ponto)
4. Destaque os 3 PRINCIPAIS BENEFÍCIOS com fontes grandes
5. Use cores VIBRANTES e CONTRASTANTES
6. Adicione BADGES de "PROMOÇÃO", "BESTSELLER", "QUALIDADE PREMIUM"
7. Fundo BRANCO ou NEUTRO para destaque máximo
8. Layout PROFISSIONAL estilo Amazon/Mercado Livre
9. Foco total em CONVERSÃO e CLIQUES
10. Textos legíveis mesmo em thumbnails pequenos
"""
        
        # Gerar imagem usando Gemini
        model = genai.GenerativeModel('gemini-1.5-pro')
        
        # Carregar imagem do produto
        produto_img = Image.open(produto_path)
        
        # Preparar conteúdo para a API
        content = [prompt, produto_img]
        
        # Se tiver template, adicionar
        if template_path:
            template_img = Image.open(template_path)
            content.append(template_img)
        
        # Gerar resposta
        response = model.generate_content(content)
        
        # Como o Gemini não gera imagens diretamente, vamos usar o Imagen
        # Primeiro, vamos pegar a descrição gerada
        descricao = response.text
        
        # Agora usar Imagen para gerar as imagens
        imagen_model = genai.ImageGenerationModel("imagen-3.0-generate-001")
        
        result = imagen_model.generate_images(
            prompt=descricao,
            number_of_images=min(num_imagens, 4),
            safety_filter_level="block_only_high",
            aspect_ratio=aspect_ratio
        )
        
        # Salvar imagens e preparar resposta
        imagens_urls = []
        
        for i, image in enumerate(result.images):
            filename = f"produto_gerado_{timestamp}_{i+1}.png"
            filepath = os.path.join(OUTPUT_FOLDER, filename)
            image.save(filepath)
            
            # Converter para base64
            img_buffer = io.BytesIO()
            image.save(img_buffer, format='PNG')
            img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
            
            imagens_urls.append({
                'url': f'/static/imagens_geradas/{filename}',
                'base64': f'data:image/png;base64,{img_base64}',
                'filename': filename
            })
        
        return jsonify({
            'sucesso': True,
            'imagens': imagens_urls,
            'prompt_usado': descricao
        })
        
    except Exception as e:
        print(f"Erro detalhado: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'sucesso': False,
            'erro': str(e)
        }), 500

@app.route('/galeria')
def galeria():
    """Listar imagens geradas"""
    try:
        arquivos = []
        if os.path.exists(OUTPUT_FOLDER):
            for filename in os.listdir(OUTPUT_FOLDER):
                if filename.endswith(('.png', '.jpg', '.jpeg')):
                    filepath = os.path.join(OUTPUT_FOLDER, filename)
                    timestamp = os.path.getmtime(filepath)
                    arquivos.append({
                        'url': f'/static/imagens_geradas/{filename}',
                        'filename': filename,
                        'timestamp': timestamp
                    })
        
        arquivos.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return jsonify({
            'sucesso': True,
            'imagens': arquivos
        })
        
    except Exception as e:
        return jsonify({
            'sucesso': False,
            'erro': str(e)
        }), 500

@app.route('/download/<filename>')
def download(filename):
    """Download de imagem"""
    try:
        filepath = os.path.join(OUTPUT_FOLDER, filename)
        return send_file(filepath, as_attachment=True)
    except Exception as e:
        return jsonify({'erro': str(e)}), 404

@app.route('/health')
def health():
    """Verificar se a API está funcionando"""
    return jsonify({
        'status': 'online',
        'api_key_configurada': bool(API_KEY)
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
