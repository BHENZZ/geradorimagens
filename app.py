#!/usr/bin/env python3
"""
Aplicação Web Flask para Gerador de Imagens de Produtos
Usando Google Gemini API corretamente
"""

from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
from google import genai
from google.genai import types
import os
import base64
from datetime import datetime
from PIL import Image
from io import BytesIO

app = Flask(__name__)
CORS(app)

# Configurar API Key
API_KEY = os.getenv("GOOGLE_API_KEY", "AIzaSyCU8tdR0ikIEu9qWZftd6LCPjk5jBn-iLQ")

# Criar cliente GenAI
client = genai.Client(api_key=API_KEY)

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
        
        template_info = ""
        if template:
            template_filename = f"template_{timestamp}.png"
            template_path = os.path.join(UPLOAD_FOLDER, template_filename)
            template.save(template_path)
            template_info = "\n- Siga o estilo visual do template fornecido"
        
        # Criar prompt otimizado para marketplaces
        prompt = f"""Crie imagens profissionais de produto para marketplace com foco em conversão.

PRODUTO: {ficha_tecnica}

ESTILO MARKETPLACE (Amazon/Mercado Livre):
- Produto em destaque centralizado
- Múltiplos ângulos (frente, lateral, detalhe)
- Fundo BRANCO limpo
- Textos CURTOS destacando benefícios principais
- Ícones visuais (✓, ⭐, 🔒) para características
- BADGES de "PREMIUM", "BESTSELLER"
- Layout profissional e clean
- Textos legíveis em miniaturas{template_info}
- Design que CONVERTE e gera CLIQUES

Crie uma composição atrativa e profissional."""
        
        # Gerar imagens usando Imagen
        try:
            response = client.models.generate_images(
                model='imagen-3.0-generate-002',
                prompt=prompt,
                config=types.GenerateImagesConfig(
                    number_of_images=min(num_imagens, 4),
                    aspect_ratio=aspect_ratio,
                    output_mime_type='image/png',
                )
            )
        except Exception as api_error:
            error_msg = str(api_error)
            print(f"Erro na API: {error_msg}")
            
            # Mensagens de erro mais amigáveis
            if "404" in error_msg or "not found" in error_msg.lower():
                return jsonify({
                    'sucesso': False,
                    'erro': 'Modelo Imagen não encontrado. Verifique se a API está ativada no Google Cloud Console e se você tem uma conta paga.'
                }), 500
            elif "403" in error_msg or "permission" in error_msg.lower():
                return jsonify({
                    'sucesso': False,
                    'erro': 'Sem permissão para usar Imagen. A geração de imagens está disponível apenas para contas pagas.'
                }), 500
            else:
                return jsonify({
                    'sucesso': False,
                    'erro': f'Erro na API do Google: {error_msg}'
                }), 500
        
        # Salvar imagens e preparar resposta
        imagens_urls = []
        
        for i, generated_image in enumerate(response.generated_images):
            filename = f"produto_{timestamp}_{i+1}.png"
            filepath = os.path.join(OUTPUT_FOLDER, filename)
            
            # Salvar imagem
            image = Image.open(BytesIO(generated_image.image.image_bytes))
            image.save(filepath)
            
            # Converter para base64
            img_base64 = base64.b64encode(generated_image.image.image_bytes).decode()
            
            imagens_urls.append({
                'url': f'/static/imagens_geradas/{filename}',
                'base64': f'data:image/png;base64,{img_base64}',
                'filename': filename
            })
        
        return jsonify({
            'sucesso': True,
            'imagens': imagens_urls,
            'prompt_usado': prompt
        })
        
    except Exception as e:
        print(f"Erro detalhado: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'sucesso': False,
            'erro': f'Erro ao gerar imagem: {str(e)}'
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
