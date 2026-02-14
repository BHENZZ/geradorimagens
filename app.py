#!/usr/bin/env python3
"""
Aplicação Web Flask para Gerador de Imagens de Produtos
Otimizado para 512MB RAM - Plano Starter Render
"""

from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
import google.genai as genai
from google.genai import types
from PIL import Image
from io import BytesIO
import os
import base64
import time
import gc
from datetime import datetime
from prompts_6_imagens import get_prompts_config

app = Flask(__name__)
CORS(app)

# Configurar API Key
API_KEY = os.getenv("GOOGLE_API_KEY", "AIzaSyCU8tdR0ikIEu9qWZftd6LCPjk5jBn-iLQ")
client = genai.Client(api_key=API_KEY)

# Criar pastas
OUTPUT_FOLDER = "static/imagens_geradas"
UPLOAD_FOLDER = "static/uploads"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/gerar', methods=['POST'])
def gerar_imagem():
    print("\n" + "="*50)
    print("🎨 INICIANDO GERAÇÃO - Modo 512MB RAM")
    print("="*50)
    
    try:
        return _gerar_imagem_internal()
    except Exception as e:
        print(f"❌ ERRO: {str(e)}")
        return jsonify({'sucesso': False, 'erro': str(e)}), 500

def _gerar_imagem_internal():
    # Validar API Key
    if not API_KEY:
        return jsonify({'sucesso': False, 'erro': 'API Key não configurada'}), 500
    
    # Pegar dados
    ficha_tecnica = request.form.get('ficha_tecnica', '')
    cor_icones = request.form.get('cor_icones', '#2563EB')
    cor_fonte = request.form.get('cor_fonte', '#1E293B')
    cor_destaque = request.form.get('cor_destaque', '#8B5CF6')
    fonte_escolhida = request.form.get('fonte', 'Inter')
    
    if not ficha_tecnica:
        return jsonify({'sucesso': False, 'erro': 'Ficha técnica obrigatória'}), 400
    
    # Extrair produto e benefícios
    linhas = [l.strip() for l in ficha_tecnica.split('\n') if l.strip()]
    produto_nome = linhas[0] if linhas else "Produto"
    beneficios = [l.lstrip('✓-•►▪︎▸▹▶▷●○◆◇■□★☆0123456789.)> ') 
                  for l in linhas[1:] if len(l.strip()) > 3]
    
    print(f"📝 Produto: {produto_nome}")
    print(f"🎯 Benefícios: {len(beneficios)}")
    
    # Timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Gerar prompts
    prompts_config = get_prompts_config(
        produto_nome, beneficios, cor_icones, 
        cor_fonte, cor_destaque, fonte_escolhida
    )
    
    # Gerar imagens UMA POR VEZ
    imagens_urls = []
    
    for i, config in enumerate(prompts_config):
        try:
            print(f"\n⏳ IMAGEM {i+1}/6 - {config['tipo']}")
            
            # Limpar memória ANTES
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
                print(f"⚠️ Sem resposta")
                continue
            
            # Extrair imagem
            image_data = None
            for part in response.candidates[0].content.parts:
                if hasattr(part, 'inline_data') and part.inline_data:
                    image_data = part.inline_data.data
                    break
            
            if not image_data:
                print(f"❌ Sem imagem")
                continue
            
            # Salvar
            filename = f"produto_{timestamp}_{i+1}_{config['tipo']}.png"
            filepath = os.path.join(OUTPUT_FOLDER, filename)
            
            with open(filepath, 'wb') as f:
                f.write(image_data)
            
            # IMPORTANTE: NÃO incluir base64 na resposta (economiza ~3-5MB!)
            imagens_urls.append({
                'url': f'/static/imagens_geradas/{filename}',
                'filename': filename,
                'tipo': config['tipo'],
                'descricao': config['descricao']
            })
            
            print(f"✅ Imagem {i+1} salva!")
            
            # Limpar IMEDIATAMENTE
            del response
            del image_data
            gc.collect()
            
            # Pausa entre imagens
            time.sleep(2)
            
        except Exception as e:
            print(f"❌ Erro imagem {i+1}: {e}")
            gc.collect()
            continue
    
    if not imagens_urls:
        raise Exception("Nenhuma imagem gerada")
    
    print(f"🎉 {len(imagens_urls)}/6 imagens OK")
    
    return jsonify({
        'sucesso': True,
        'imagens': imagens_urls,
        'total_geradas': len(imagens_urls)
    })

@app.route('/galeria')
def galeria():
    try:
        arquivos = []
        if os.path.exists(OUTPUT_FOLDER):
            for filename in os.listdir(OUTPUT_FOLDER):
                if filename.endswith(('.png', '.jpg', '.jpeg')):
                    arquivos.append({
                        'url': f'/static/imagens_geradas/{filename}',
                        'filename': filename
                    })
        return jsonify({'sucesso': True, 'imagens': arquivos})
    except Exception as e:
        return jsonify({'sucesso': False, 'erro': str(e)}), 500

@app.route('/download/<filename>')
def download(filename):
    try:
        return send_file(os.path.join(OUTPUT_FOLDER, filename), as_attachment=True)
    except Exception as e:
        return jsonify({'erro': str(e)}), 404

@app.route('/health')
def health():
    try:
        api_ok = bool(API_KEY) and len(API_KEY) > 20
        gemini_ok = False
        try:
            client.models.list()
            gemini_ok = True
        except:
            pass
        
        return jsonify({
            'status': 'online' if (api_ok and gemini_ok) else 'error',
            'api_key_configurada': api_ok,
            'gemini_conectado': gemini_ok,
            'ram': '512MB',
            'modelo': 'gemini-2.5-flash-image'
        })
    except Exception as e:
        return jsonify({'status': 'error', 'erro': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
