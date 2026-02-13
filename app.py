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
    """Endpoint para gerar imagem usando Nano Banana (versão GRÁTIS)"""
    try:
        # Pegar dados do formulário
        ficha_tecnica = request.form.get('ficha_tecnica', '')
        num_imagens = int(request.form.get('num_imagens', 1))
        
        if not ficha_tecnica:
            return jsonify({'erro': 'Ficha técnica é obrigatória'}), 400
        
        # Timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Criar prompt otimizado e CURTO (importante para o modelo grátis)
        prompt = f"""Create a professional product image for e-commerce marketplace.

PRODUCT: {ficha_tecnica}

Style: Clean white background, product centered, professional lighting, high quality, sharp details, e-commerce style like Amazon.

Make it attractive and professional."""

        print(f"🎨 Gerando {num_imagens} imagem(ns)...")
        print(f"📝 Prompt: {prompt[:100]}...")
        
        # USAR NANO BANANA (Versão GRÁTIS - Gemini 2.5 Flash Image)
        imagens_urls = []
        
        for i in range(min(num_imagens, 4)):
            try:
                print(f"⏳ Gerando imagem {i+1}/{num_imagens}...")
                
                # Chamar API do Nano Banana (GRÁTIS)
                response = client.models.generate_content(
                    model='gemini-2.5-flash-image',  # Modelo GRÁTIS
                    contents=[prompt],
                    config=types.GenerateContentConfig(
                        response_modalities=["IMAGE"],
                        temperature=0.9,
                    )
                )
                
                print(f"✅ Response recebida para imagem {i+1}")
                
                # Verificar se há resposta
                if not response or not response.candidates:
                    raise Exception("API não retornou candidatos")
                
                # Extrair imagem do response
                image_data = None
                for part in response.candidates[0].content.parts:
                    if hasattr(part, 'inline_data') and part.inline_data:
                        image_data = part.inline_data.data
                        print(f"📦 Dados da imagem encontrados: {len(image_data)} bytes")
                        break
                
                if not image_data:
                    print(f"⚠️ Nenhuma imagem gerada no response")
                    # Tentar pegar de outra forma
                    if hasattr(response.candidates[0].content.parts[0], 'text'):
                        raise Exception(f"API retornou texto: {response.candidates[0].content.parts[0].text}")
                    raise Exception("Nenhuma imagem foi gerada pela API")
                
                # Salvar imagem
                filename = f"produto_{timestamp}_{i+1}.png"
                filepath = os.path.join(OUTPUT_FOLDER, filename)
                
                # Salvar arquivo
                with open(filepath, 'wb') as f:
                    f.write(image_data)
                
                print(f"💾 Imagem salva: {filepath}")
                
                # Converter para base64
                img_base64 = base64.b64encode(image_data).decode()
                
                imagens_urls.append({
                    'url': f'/static/imagens_geradas/{filename}',
                    'base64': f'data:image/png;base64,{img_base64}',
                    'filename': filename
                })
                
                print(f"✅ Imagem {i+1} processada com sucesso!")
                
            except Exception as img_error:
                print(f"❌ Erro ao gerar imagem {i+1}: {str(img_error)}")
                import traceback
                traceback.print_exc()
                continue
        
        if not imagens_urls:
            raise Exception("Nenhuma imagem foi gerada com sucesso. Verifique se a API está habilitada e se você tem quota disponível.")
        
        print(f"🎉 Sucesso! {len(imagens_urls)} imagem(ns) gerada(s)")
        
        return jsonify({
            'sucesso': True,
            'imagens': imagens_urls,
            'prompt_usado': prompt
        })
        
    except Exception as e:
        print(f"❌ Erro geral: {str(e)}")
        import traceback
        traceback.print_exc()
        
        error_msg = str(e)
        
        # Mensagens de erro mais amigáveis
        if "quota" in error_msg.lower() or "limit" in error_msg.lower():
            error_msg = "Limite de quota excedido. Você atingiu o limite de 500 imagens/dia grátis. Tente novamente amanhã ou configure billing."
        elif "permission" in error_msg.lower() or "403" in error_msg:
            error_msg = "Sem permissão. Verifique se a Gemini API está habilitada no Google AI Studio."
        elif "not found" in error_msg.lower() or "404" in error_msg:
            error_msg = "Modelo não encontrado. Verifique se você tem acesso ao Gemini API."
        elif "api key" in error_msg.lower():
            error_msg = "API Key inválida. Verifique se configurou corretamente no Render."
        
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
        'limite_diario': '500 imagens/dia'
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
