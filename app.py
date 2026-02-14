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
from datetime import datetime
from prompts_6_imagens import get_prompts_config

app = Flask(__name__)
CORS(app)

# Configurar API Key - CORRETA (verificada 2025-02-14)
# ATENÇÃO: Esta é a API Key CORRETA com "0ikI" (não "0lKl")
API_KEY = os.getenv("GOOGLE_API_KEY", "AIzaSyCU8tdR0ikIEu9qWZftd6LCPjk5jBn-iLQ")
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
    print("\n" + "="*50)
    print("🎨 INICIANDO GERAÇÃO DE IMAGENS")
    print("="*50)
    
    # IMPORTANTE: Garantir que SEMPRE retorna JSON
    try:
        return _gerar_imagem_internal()
    except Exception as e:
        print(f"❌ ERRO CRÍTICO: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Garantir resposta JSON mesmo em erro crítico
        return jsonify({
            'sucesso': False,
            'erro': f'Erro no servidor: {str(e)}'
        }), 500

def _gerar_imagem_internal():
    """Lógica interna de geração (separada para tratamento de erro)"""
    try:
        # Validar API Key
        print(f"🔑 Verificando API Key...")
        print(f"API Key configurada: {bool(API_KEY)}")
        print(f"API Key primeiros caracteres: {API_KEY[:20] if API_KEY else 'NENHUMA'}...")
        
        if not API_KEY or API_KEY == "":
            print("❌ API Key não configurada!")
            return jsonify({
                'sucesso': False,
                'erro': 'API Key não configurada. Configure GOOGLE_API_KEY no Render.'
            }), 500
        
        # Pegar dados do formulário
        print(f"\n📋 Coletando dados do formulário...")
        ficha_tecnica = request.form.get('ficha_tecnica', '')
        cor_icones = request.form.get('cor_icones', '#2563EB')
        cor_fonte = request.form.get('cor_fonte', '#1E293B')
        cor_destaque = request.form.get('cor_destaque', '#8B5CF6')
        fonte_escolhida = request.form.get('fonte', 'Inter')
        
        print(f"Ficha técnica: {len(ficha_tecnica)} caracteres")
        print(f"Cores: {cor_icones}, {cor_fonte}, {cor_destaque}")
        print(f"Fonte: {fonte_escolhida}")
        
        # Verificar se tem imagem do produto
        imagem_produto_base64 = None
        imagem_produto_mime = None
        
        if 'imagem_produto' in request.files:
            file = request.files['imagem_produto']
            if file and file.filename != '':
                print(f"📸 Imagem do produto recebida!")
                print(f"   Nome: {file.filename}")
                print(f"   Content-Type: {file.content_type}")
                
                try:
                    # Ler e converter para base64
                    img_bytes = file.read()
                    print(f"   Tamanho: {len(img_bytes)} bytes")
                    
                    # Converter para base64 (módulo já importado no topo)
                    imagem_produto_base64 = base64.b64encode(img_bytes).decode('utf-8')
                    imagem_produto_mime = file.content_type or 'image/jpeg'
                    
                    print(f"✅ Imagem convertida para base64: {len(imagem_produto_base64)} chars")
                    print(f"   MIME Type: {imagem_produto_mime}")
                    
                    # TODO: Integrar imagem nos prompts (próxima versão)
                    # Por enquanto apenas validamos que o upload funciona
                    
                except Exception as img_error:
                    print(f"⚠️ Erro ao processar imagem: {str(img_error)}")
                    # Não falhar se der erro no upload - continuar sem imagem
        else:
            print(f"📸 Nenhuma imagem do produto enviada (opcional)")
        
        if not ficha_tecnica:
            print("❌ Ficha técnica vazia!")
            return jsonify({
                'sucesso': False,
                'erro': 'Ficha técnica é obrigatória'
            }), 400
        
        print(f"\n🔧 Inicializando cliente Gemini...")
        try:
            # Testar se o cliente funciona
            print(f"📡 Testando conexão com API...")
            test_response = client.models.list()
            print(f"✅ Cliente Gemini inicializado com sucesso!")
        except Exception as client_error:
            print(f"❌ Erro ao inicializar cliente: {str(client_error)}")
            return jsonify({
                'sucesso': False,
                'erro': f'Erro ao conectar com Gemini API: {str(client_error)}'
            }), 500
        
        # Timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Dividir ficha técnica em linhas e extrair benefícios AUTOMATICAMENTE
        linhas_ficha = [linha.strip() for linha in ficha_tecnica.split('\n') if linha.strip()]
        
        # Primeira linha = Nome do produto
        produto_nome = linhas_ficha[0] if linhas_ficha else "Produto"
        
        # Extrair benefícios automaticamente (qualquer linha que não seja a primeira)
        # Aceita linhas com ✓, -, •, números, ou qualquer texto
        beneficios = []
        for linha in linhas_ficha[1:]:
            # Limpar caracteres especiais do início
            linha_limpa = linha.lstrip('✓-•►▪︎▸▹▶▷●○◆◇■□★☆0123456789.)> ')
            if linha_limpa and len(linha_limpa) > 3:  # Ignorar linhas muito curtas
                beneficios.append(linha_limpa)
        
        print(f"📝 Produto: {produto_nome}")
        print(f"🎯 Benefícios extraídos automaticamente: {len(beneficios)}")
        for i, b in enumerate(beneficios[:5], 1):
            print(f"   {i}. {b}")
        
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
        
        # Gerar as 6 imagens UMA POR VEZ (para não estourar memória)
        imagens_urls = []
        
        print(f"\n{'='*60}")
        print(f"🎨 INICIANDO GERAÇÃO DAS 6 IMAGENS")
        print(f"{'='*60}")
        
        for i, config in enumerate(prompts_config):
            try:
                print(f"\n{'─'*60}")
                print(f"⏳ IMAGEM {i+1}/6 - {config['tipo']}")
                print(f"{'─'*60}")
                
                print(f"📝 Prompt (primeiros 150 chars):")
                print(f"   {config['prompt'][:150]}...")
                
                print(f"\n🔧 Chamando API Gemini...")
                print(f"   Modelo: gemini-2.5-flash-image")
                print(f"   Temperature: 0.9")
                
                # Chamar API
                try:
                    response = client.models.generate_content(
                        model='gemini-2.5-flash-image',
                        contents=[config['prompt']],
                        config=types.GenerateContentConfig(
                            response_modalities=["IMAGE"],
                            temperature=0.9,
                        )
                    )
                    print(f"✅ API respondeu!")
                    
                except Exception as api_error:
                    print(f"❌ ERRO NA CHAMADA DA API:")
                    print(f"   Tipo: {type(api_error).__name__}")
                    print(f"   Mensagem: {str(api_error)}")
                    raise
                
                # Verificar resposta
                if not response:
                    print(f"⚠️ Response é None!")
                    continue
                    
                print(f"📦 Response object: {type(response)}")
                
                if not hasattr(response, 'candidates'):
                    print(f"⚠️ Response não tem atributo 'candidates'!")
                    continue
                    
                if not response.candidates:
                    print(f"⚠️ Response.candidates está vazio!")
                    continue
                
                print(f"✅ Response tem {len(response.candidates)} candidate(s)")
                
                # Extrair imagem
                print(f"\n🔍 Procurando imagem nos parts...")
                image_data = None
                
                for part_idx, part in enumerate(response.candidates[0].content.parts):
                    print(f"   Part {part_idx}: {type(part)}")
                    
                    if hasattr(part, 'inline_data'):
                        if part.inline_data:
                            image_data = part.inline_data.data
                            print(f"   ✅ IMAGEM ENCONTRADA no part {part_idx}!")
                            print(f"   📦 Tamanho: {len(image_data)} bytes")
                            break
                        else:
                            print(f"   ⚠️ Part tem inline_data mas está None")
                    else:
                        print(f"   ⚠️ Part não tem inline_data")
                
                if not image_data:
                    print(f"❌ Nenhuma imagem encontrada nos {len(response.candidates[0].content.parts)} parts")
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
                
                # IMPORTANTE: Limpar variáveis para liberar memória (com segurança)
                try:
                    del response
                except: pass
                try:
                    del image_data
                except: pass
                try:
                    del img_base64
                except: pass
                
                # Force garbage collection
                import gc
                gc.collect()
                
                print(f"🧹 Memória liberada após imagem {i+1}")
                
            except Exception as img_error:
                print(f"❌ Erro na imagem {i+1}: {str(img_error)}")
                import traceback
                traceback.print_exc()
                
                # Liberar memória mesmo em caso de erro (com segurança)
                try:
                    del response
                except: pass
                try:
                    del image_data  
                except: pass
                
                import gc
                gc.collect()
                
                # Continuar tentando as próximas imagens
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

@app.route('/debug')
def debug():
    """Endpoint de debug detalhado"""
    try:
        debug_info = {
            'status': 'running',
            'api_key': {
                'configurada': bool(API_KEY),
                'tamanho': len(API_KEY) if API_KEY else 0,
                'preview': API_KEY[:25] + '...' if API_KEY and len(API_KEY) > 25 else 'NENHUMA',
                'tem_0ikI': '0ikI' in API_KEY if API_KEY else False
            },
            'teste_completo': {}
        }
        
        # Testar geração completa
        try:
            print("\n🧪 DEBUG: Testando geração completa...")
            
            # Prompt de teste
            test_prompt = "A simple red square on white background"
            
            print(f"📝 Prompt: {test_prompt}")
            
            # Gerar
            response = client.models.generate_content(
                model='gemini-2.5-flash-image',
                contents=[test_prompt],
                config=types.GenerateContentConfig(
                    response_modalities=["IMAGE"],
                    temperature=0.9,
                )
            )
            
            print(f"✅ Response recebida")
            
            debug_info['teste_completo']['success'] = True
            debug_info['teste_completo']['has_candidates'] = bool(response.candidates)
            
            if response.candidates:
                debug_info['teste_completo']['num_candidates'] = len(response.candidates)
                debug_info['teste_completo']['num_parts'] = len(response.candidates[0].content.parts)
                
                # Verificar se tem imagem
                has_image = False
                for part in response.candidates[0].content.parts:
                    if hasattr(part, 'inline_data') and part.inline_data:
                        debug_info['teste_completo']['image_size'] = len(part.inline_data.data)
                        has_image = True
                        break
                
                debug_info['teste_completo']['has_image'] = has_image
            
        except Exception as e:
            debug_info['teste_completo']['success'] = False
            debug_info['teste_completo']['error'] = str(e)
            debug_info['teste_completo']['error_type'] = type(e).__name__
        
        return jsonify(debug_info)
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'erro': str(e)
        }), 500

@app.route('/health')
def health():
    """Verificar se a API está funcionando"""
    try:
        # Testar API Key
        api_key_ok = bool(API_KEY) and len(API_KEY) > 20
        
        # Testar conexão com Gemini
        gemini_ok = False
        gemini_error = None
        try:
            test_response = client.models.list()
            gemini_ok = True
        except Exception as e:
            gemini_error = str(e)
        
        return jsonify({
            'status': 'online' if (api_key_ok and gemini_ok) else 'error',
            'api_key_configurada': api_key_ok,
            'api_key_preview': API_KEY[:20] + '...' if API_KEY else 'NENHUMA',
            'gemini_conectado': gemini_ok,
            'gemini_error': gemini_error,
            'modelo': 'gemini-2.5-flash-image (Nano Banana - GRÁTIS)',
            'limite_diario': '500 imagens/dia',
            'imagens_por_request': 6
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'erro': str(e)
        }), 500

@app.route('/test-api')
def test_api():
    """Testar geração de uma imagem simples"""
    try:
        print("\n🧪 TESTE DE API")
        print("="*50)
        
        # Prompt simples de teste
        test_prompt = "A simple red circle on white background"
        
        print(f"📝 Prompt de teste: {test_prompt}")
        print(f"🔑 API Key: {API_KEY[:20]}...")
        
        # Tentar gerar
        response = client.models.generate_content(
            model='gemini-2.5-flash-image',
            contents=[test_prompt],
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE"],
                temperature=0.9,
            )
        )
        
        print(f"✅ Response recebida!")
        print(f"📊 Candidates: {len(response.candidates) if response.candidates else 0}")
        
        if response.candidates:
            print(f"📦 Parts: {len(response.candidates[0].content.parts)}")
        
        return jsonify({
            'sucesso': True,
            'mensagem': 'API funcionando! Imagem de teste gerada com sucesso.',
            'candidates': len(response.candidates) if response.candidates else 0
        })
        
    except Exception as e:
        print(f"❌ Erro no teste: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            'sucesso': False,
            'erro': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
