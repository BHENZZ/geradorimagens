#!/usr/bin/env python3
"""
Script para diagnosticar o problema no Render
"""

import os

print("="*70)
print("🔍 DIAGNÓSTICO COMPLETO")
print("="*70)

# 1. Verificar API Key
api_key = os.getenv("GOOGLE_API_KEY", "")
print(f"\n1️⃣ API KEY:")
print(f"   Configurada: {bool(api_key)}")
print(f"   Tamanho: {len(api_key)} caracteres")
print(f"   Preview: {api_key[:30]}...{api_key[-10:] if len(api_key) > 40 else ''}")

# Caracteres específicos que diferenciam as duas keys
if "0ikI" in api_key:
    print(f"   ✅ API Key CORRETA (contém '0ikI')")
elif "0lKl" in api_key:
    print(f"   ❌ API Key ERRADA (contém '0lKl')")
else:
    print(f"   ⚠️ API Key desconhecida")

# 2. Testar importação
print(f"\n2️⃣ IMPORTAÇÕES:")
try:
    import google.genai as genai
    from google.genai import types
    print(f"   ✅ google.genai importado com sucesso")
except Exception as e:
    print(f"   ❌ Erro ao importar: {e}")
    exit(1)

# 3. Testar cliente
print(f"\n3️⃣ CLIENTE GEMINI:")
try:
    client = genai.Client(api_key=api_key)
    print(f"   ✅ Cliente criado com sucesso")
except Exception as e:
    print(f"   ❌ Erro ao criar cliente: {e}")
    exit(1)

# 4. Listar modelos
print(f"\n4️⃣ MODELOS DISPONÍVEIS:")
try:
    models_list = list(client.models.list())
    print(f"   ✅ {len(models_list)} modelos encontrados")
    
    # Procurar por modelos de imagem
    image_models = [m for m in models_list if 'image' in m.name.lower()]
    if image_models:
        print(f"   📸 Modelos de imagem:")
        for m in image_models[:5]:
            print(f"      - {m.name}")
except Exception as e:
    print(f"   ❌ Erro ao listar modelos: {e}")

# 5. Testar geração
print(f"\n5️⃣ TESTE DE GERAÇÃO:")
try:
    print(f"   Gerando imagem de teste...")
    response = client.models.generate_content(
        model='gemini-2.5-flash-image',
        contents=["A simple red circle on white background"],
        config=types.GenerateContentConfig(
            response_modalities=["IMAGE"],
            temperature=0.9,
        )
    )
    
    print(f"   ✅ Response recebida")
    
    if response.candidates:
        print(f"   ✅ {len(response.candidates)} candidate(s)")
        
        # Verificar se tem imagem
        has_image = False
        for part in response.candidates[0].content.parts:
            if hasattr(part, 'inline_data') and part.inline_data:
                print(f"   ✅ Imagem encontrada! {len(part.inline_data.data)} bytes")
                has_image = True
                break
        
        if not has_image:
            print(f"   ⚠️ Response sem imagem")
    else:
        print(f"   ⚠️ Response sem candidates")
        
except Exception as e:
    print(f"   ❌ Erro na geração: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*70)
print("🏁 DIAGNÓSTICO COMPLETO")
print("="*70)
