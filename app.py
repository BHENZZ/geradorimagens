#!/usr/bin/env python3
"""
Aplicação Web Flask para Gerador de Imagens Google Gemini
Para rodar: python app.py
"""

from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
import google.generativeai as genai
import os
import io
import base64
from datetime import datetime
from PIL import Image

app = Flask(__name__)
CORS(app)

# Configurar API Key - IMPORTANTE: Em produção, use variável de ambiente!
API_KEY = os.getenv("GOOGLE_API_KEY", "AIzaSyCU8tdR0ikIEu9qWZftd6LCPjk5jBn-iLQ")
genai.configure(api_key=API_KEY)

# Criar pasta para salvar imagens
OUTPUT_FOLDER = "static/imagens_geradas"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route('/')
def index():
    """Página principal"""
    return render_template('index.html')

@app.route('/gerar', methods=['POST'])
def gerar_imagem():
    """Endpoint para gerar imagem"""
    try:
        data = request.json
        prompt = data.get('prompt', '')
        num_imagens = int(data.get('num_imagens', 1))
        aspect_ratio = data.get('aspect_ratio', '1:1')
        
        if not prompt:
            return jsonify({'erro': 'Prompt vazio'}), 400
        
        if num_imagens < 1 or num_imagens > 4:
            return jsonify({'erro': 'Número de imagens deve ser entre 1 e 4'}), 400
        
        # Gerar imagem usando Gemini
        model = genai.ImageGenerationModel("imagen-3.0-generate-001")
        
        result = model.generate_images(
            prompt=prompt,
            number_of_images=num_imagens,
            safety_filter_level="block_only_high",
            person_generation="allow_adult",
            aspect_ratio=aspect_ratio,
            negative_prompt="ugly, blurry, low quality, distorted"
        )
        
        # Salvar imagens e preparar resposta
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        imagens_urls = []
        
        for i, image in enumerate(result.images):
            filename = f"imagem_{timestamp}_{i+1}.png"
            filepath = os.path.join(OUTPUT_FOLDER, filename)
            image.save(filepath)
            
            # Converter para base64 para enviar ao frontend
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
            'prompt': prompt
        })
        
    except Exception as e:
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
        
        # Ordenar por data (mais recentes primeiro)
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
    # Para desenvolvimento local
    app.run(debug=True, host='0.0.0.0', port=5000)
