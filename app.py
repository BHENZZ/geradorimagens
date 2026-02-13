#!/usr/bin/env python3
"""
Aplicação Web Flask para Gerador de Imagens de Produtos
Usando Nano Banana Pro (Gemini 3 Pro Image)
"""

from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
import google.genai as genai
from google.genai import types
from PIL import Image
from io import BytesIO
import os
import base64
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Configurar API Key
API_KEY = os.getenv("GOOGLE_API_KEY", "AIzaSyCU8tdR0lKlEu9qWZftd6LCPjk5jBn-iLQ")
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
    """Endpoint para gerar imagem usando Nano Banana Pro"""
    try:
        # Pegar dados do formulário
        ficha_tecnica = request.form.get('ficha_tecnica', '')
        num_imagens = int(request.form.get('num_imagens', 1))
        aspect_ratio = request.form.get('aspect_ratio', '1:1')
        
        if not ficha_tecnica:
            return jsonify({'erro': 'Ficha técnica é obrigatória'}), 400
        
        # Timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Criar prompt otimizado para marketplaces
        prompt = f"""Crie uma imagem profissional de produto para marketplace com foco em conversão.

PRODUTO: {ficha_tecnica}

INSTRUÇÕES PARA ALTA CONVERSÃO:
- Produto em destaque centralizado
- Fundo BRANCO limpo e profissional
- Textos CURTOS destacando benefícios principais
- Ícones visuais (✓, ⭐, 🔒) para características
- BADGES de "PREMIUM", "BESTSELLER" se aplicável
- Layout profissional estilo Amazon/Mercado Livre
- Textos legíveis mesmo em miniaturas
- Design que CONVERTE e gera CLIQUES

Crie uma composição atrativa, moderna e profissional."""

        # Mapear aspect ratio para o formato do Gemini
        resolution = "1K"  # Default 1024x1024
        
        # USAR NANO BANANA PRO (Gemini 3 Pro Image)
        # Gerar múltiplas imagens
        imagens_urls = []
        
        for i in range(min(num_imagens, 4)):
            try:
                # Chamar API do Nano Banana Pro
                response = client.models.generate_content(
                    model='gemini-3-pro-image-preview',  # Nano Banana Pro
                    contents=[prompt],
                    config=types.GenerateContentConfig(
                        response_modalities=["IMAGE"],
                        temperature=1.0,
                    )
                )
                
                # Extrair imagem do response
                image_data = None
                for part in response.candidates[0].content.parts:
                    if hasattr(part, 'inline_data') and part.inline_data:
                        image_data = part.inline_data.data
                        break
                
                if not image_data:
                    raise Exception("Nenhuma imagem foi gerada")
                
                # Salvar imagem
                filename = f"produto_{timestamp}_{i+1}.png"
                filepath = os.path.join(OUTPUT_FOLDER, filename)
                
                # Salvar arquivo
                with open(filepath, 'wb') as f:
                    f.write(image_data)
                
                # Converter para base64
                img_base64 = base64.b64encode(image_data).decode()
                
                imagens_urls.append({
                    'url': f'/static/imagens_geradas/{filename}',
                    'base64': f'data:image/png;base64,{img_base64}',
                    'filename': filename
                })
                
            except Exception as img_error:
                print(f"Erro ao gerar imagem {i+1}: {str(img_error)}")
                continue
        
        if not imagens_urls:
            raise Exception("Nenhuma imagem foi gerada com sucesso")
        
        return jsonify({
            'sucesso': True,
            'imagens': imagens_urls,
            'prompt_usado': prompt
        })
        
    except Exception as e:
        print(f"Erro detalhado: {str(e)}")
        import traceback
        traceback.print_exc()
        
        error_msg = str(e)
        if "quota" in error_msg.lower():
            error_msg = "Limite de quota excedido. Aguarde alguns minutos ou verifique seu plano."
        elif "permission" in error_msg.lower() or "403" in error_msg:
            error_msg = "Sem permissão. Verifique se a API está habilitada e se você tem uma conta paga."
        elif "not found" in error_msg.lower() or "404" in error_msg:
            error_msg = "Modelo não encontrado. Verifique se você tem acesso ao Nano Banana Pro."
        
        return jsonify({
            'sucesso': False,
            'erro': f'Erro ao gerar imagem: {error_msg}'
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
        'api_key_configurada': bool(API_KEY),
        'modelo': 'gemini-3-pro-image-preview (Nano Banana Pro)'
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
