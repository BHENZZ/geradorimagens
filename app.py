#!/usr/bin/env python3
"""
Gerador de Imagens - OTIMIZADO PARA 512MB RAM
Gera 3 imagens de alta qualidade
"""

from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
import google.genai as genai
from google.genai import types
import os
import base64
import time
import gc
from datetime import datetime
from prompts_6_imagens import get_prompts_config

app = Flask(__name__)
CORS(app)

API_KEY = os.getenv("GOOGLE_API_KEY", "AIzaSyCU8tdR0ikIEu9qWZftd6LCPjk5jBn-iLQ")
client = genai.Client(api_key=API_KEY)

OUTPUT_FOLDER = "static/imagens_geradas"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/gerar', methods=['POST'])
def gerar_imagem():
    try:
        # Validar
        if not API_KEY:
            return jsonify({'sucesso': False, 'erro': 'API Key não configurada'}), 500
        
        ficha_tecnica = request.form.get('ficha_tecnica', '')
        if not ficha_tecnica:
            return jsonify({'sucesso': False, 'erro': 'Ficha técnica obrigatória'}), 400
        
        # Extrair dados
        linhas = [l.strip() for l in ficha_tecnica.split('\n') if l.strip()]
        produto_nome = linhas[0] if linhas else "Produto"
        beneficios = [l.lstrip('✓-•►▪︎▸▹▶▷●○◆◇■□★☆0123456789.)> ') 
                      for l in linhas[1:] if len(l.strip()) > 3]
        
        cor_icones = request.form.get('cor_icones', '#2563EB')
        cor_fonte = request.form.get('cor_fonte', '#1E293B')
        cor_destaque = request.form.get('cor_destaque', '#8B5CF6')
        fonte = request.form.get('fonte', 'Inter')
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Gerar prompts
        prompts_config = get_prompts_config(
            produto_nome, beneficios, cor_icones, cor_fonte, cor_destaque, fonte
        )
        
        # GERAR APENAS 3 IMAGENS (mais rápido e estável)
        imagens = []
        
        for i in range(3):  # Apenas 3!
            config = prompts_config[i]
            
            print(f"⏳ Imagem {i+1}/3 - {config['tipo']}")
            
            # Limpar antes
            gc.collect()
            
            # Gerar
            response = client.models.generate_content(
                model='gemini-2.5-flash-image',
                contents=[config['prompt']],
                config=types.GenerateContentConfig(
                    response_modalities=["IMAGE"],
                    temperature=0.9,
                )
            )
            
            if not response or not response.candidates:
                continue
            
            # Extrair
            image_data = None
            for part in response.candidates[0].content.parts:
                if hasattr(part, 'inline_data') and part.inline_data:
                    image_data = part.inline_data.data
                    break
            
            if not image_data:
                continue
            
            # Salvar
            filename = f"produto_{timestamp}_{i+1}_{config['tipo']}.png"
            with open(os.path.join(OUTPUT_FOLDER, filename), 'wb') as f:
                f.write(image_data)
            
            imagens.append({
                'url': f'/static/imagens_geradas/{filename}',
                'filename': filename,
                'tipo': config['tipo'],
                'descricao': config['descricao']
            })
            
            print(f"✅ Salva!")
            
            # Limpar
            del response, image_data
            gc.collect()
            time.sleep(1)
        
        if not imagens:
            raise Exception("Nenhuma imagem gerada")
        
        return jsonify({
            'sucesso': True,
            'imagens': imagens,
            'total_geradas': len(imagens)
        })
        
    except Exception as e:
        print(f"❌ ERRO: {e}")
        return jsonify({'sucesso': False, 'erro': str(e)}), 500

@app.route('/health')
def health():
    return jsonify({'status': 'online', 'ram': '512MB', 'imagens': '3'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
