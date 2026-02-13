#!/usr/bin/env python3
"""
Aplicação Web Flask para Gerador de Imagens de Produtos
Gera 5 imagens diferentes com customização de cores e fontes
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
from prompts_6_imagens import get_prompts_config

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
    """Endpoint para gerar 6 imagens diferentes do produto"""
    try:
        # Pegar dados do formulário
        ficha_tecnica = request.form.get('ficha_tecnica', '')
        cor_icones = request.form.get('cor_icones', '#2563EB')
        cor_fonte = request.form.get('cor_fonte', '#1E293B')
        cor_destaque = request.form.get('cor_destaque', '#8B5CF6')
        fonte_escolhida = request.form.get('fonte', 'Inter')
        
        if not ficha_tecnica:
            return jsonify({'erro': 'Ficha técnica é obrigatória'}), 400
        
        # Timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Dividir ficha técnica em linhas
        linhas_ficha = [linha.strip() for linha in ficha_tecnica.split('\n') if linha.strip()]
        produto_nome = linhas_ficha[0] if linhas_ficha else "Produto"
        beneficios = [l for l in linhas_ficha[1:] if l.startswith('✓') or l.startswith('-')]
        
        print(f"🎨 Gerando 6 imagens diferentes do produto...")
        print(f"📝 Produto: {produto_nome}")
        print(f"🎯 Benefícios encontrados: {len(beneficios)}")
        print(f"🎨 Cores: Ícones={cor_icones}, Fonte={cor_fonte}, Destaque={cor_destaque}")
        print(f"🔤 Fonte: {fonte_escolhida}")
        
        # Obter configuração dos 6 prompts otimizados (arquivo prompts_6_imagens.py)
        prompts_config = get_prompts_config(
            produto_nome, 
            beneficios, 
            cor_icones, 
            cor_fonte, 
            cor_destaque, 
            fonte_escolhida
        )
        
        # Gerar as 6 imagens
        imagens_urls = []
        
        for i, config in enumerate(prompts_config):
            try:
                print(f"⏳ Gerando imagem {i+1}/6 - {config['tipo']}...")
                
                # Chamar API
                response = client.models.generate_content(
                    model='gemini-2.5-flash-image',
                    contents=[config['prompt']],
                    config=types.GenerateContentConfig(
                        response_modalities=["IMAGE"],
                        temperature=0.9,
                    )
                )
                
                print(f"✅ Response recebida para {config['tipo']}")
                
                # Verificar resposta
                if not response or not response.candidates:
                    raise Exception("API não retornou candidatos")
                
                # Extrair imagem
                image_data = None
                for part in response.candidates[0].content.parts:
                    if hasattr(part, 'inline_data') and part.inline_data:
                        image_data = part.inline_data.data
                        print(f"📦 Dados encontrados: {len(image_data)} bytes")
                        break
                
                if not image_data:
                    print(f"⚠️ Nenhuma imagem gerada para {config['tipo']}")
                    continue
                
                # Salvar imagem
                filename = f"produto_{timestamp}_{i+1}_{config['tipo']}.png"
                filepath = os.path.join(OUTPUT_FOLDER, filename)
                
                with open(filepath, 'wb') as f:
                    f.write(image_data)
                
                print(f"💾 Salvo: {filename}")
                
                # Converter para base64
                img_base64 = base64.b64encode(image_data).decode()
                
                imagens_urls.append({
                    'url': f'/static/imagens_geradas/{filename}',
                    'base64': f'data:image/png;base64,{img_base64}',
                    'filename': filename,
                    'tipo': config['tipo'],
                    'descricao': config['descricao']
                })
                
                print(f"✅ Imagem {i+1} ({config['tipo']}) concluída!")
                
            except Exception as img_error:
                print(f"❌ Erro na imagem {i+1}: {str(img_error)}")
                import traceback
                traceback.print_exc()
                continue
        
        if not imagens_urls:
            raise Exception("Nenhuma imagem foi gerada com sucesso.")
        
        print(f"🎉 Sucesso! {len(imagens_urls)}/6 imagens geradas")
        
        return jsonify({
            'sucesso': True,
            'imagens': imagens_urls,
            'total_geradas': len(imagens_urls)
        })
        
    except Exception as e:
        print(f"❌ Erro geral: {str(e)}")
        import traceback
        traceback.print_exc()
        
        error_msg = str(e)
        
        if "quota" in error_msg.lower() or "limit" in error_msg.lower():
            error_msg = "Limite de quota excedido. Limite: 500 imagens/dia grátis."
        elif "permission" in error_msg.lower() or "403" in error_msg:
            error_msg = "Sem permissão. Verifique se a Gemini API está habilitada."
        elif "not found" in error_msg.lower() or "404" in error_msg:
            error_msg = "Modelo não encontrado. Verifique acesso ao Gemini API."
        elif "api key" in error_msg.lower():
            error_msg = "API Key inválida. Verifique configuração."
        
        return jsonify({
            'sucesso': False,
            'erro': error_msg
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
        'modelo': 'gemini-2.5-flash-image (Nano Banana - GRÁTIS)',
        'limite_diario': '500 imagens/dia',
        'imagens_por_request': 6
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
