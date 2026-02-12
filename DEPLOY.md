# 🌐 Guia de Deploy - Gerador de Imagens AI

Este guia mostra como colocar sua aplicação online para que outras pessoas possam usar.

## 📋 Opções de Hospedagem

### 🥇 Opção 1: Render (RECOMENDADO - GRÁTIS)

**Vantagens:** Gratuito, fácil, SSL automático
**Limitações:** Dorme após 15min de inatividade

#### Passos:

1. Criar conta no Render: https://render.com
2. No dashboard, clique em "New +" > "Web Service"
3. Conecte seu repositório GitHub ou faça upload
4. Configure:
   - Name: `gerador-imagens-ai`
   - Environment: `Python 3`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`
5. Adicione variável de ambiente: `GOOGLE_API_KEY`
6. Clique em "Create Web Service"

URL final: https://gerador-imagens-ai.onrender.com

---

### 🥈 Opção 2: Railway

1. Criar conta: https://railway.app
2. New Project > Deploy from GitHub
3. Adicionar variável: `GOOGLE_API_KEY`
4. Deploy automático

---

### 🥉 Opção 3: PythonAnywhere

1. Criar conta: https://www.pythonanywhere.com
2. Upload dos arquivos
3. Criar Web App (Flask)
4. Configurar WSGI e reload

---

## 🔐 Segurança da API Key

**NUNCA comite a API Key no código!**

Use variável de ambiente:
```python
import os
API_KEY = os.getenv("GOOGLE_API_KEY")
```

---

## 📦 Arquivos Necessários

Já estão incluídos no projeto:
- ✅ requirements.txt
- ✅ Procfile
- ✅ .gitignore
- ✅ Dockerfile

---

## 🛡️ Checklist

- [ ] API Key em variável de ambiente
- [ ] HTTPS habilitado
- [ ] Rate limiting configurado
- [ ] Monitoramento de custos
- [ ] Termos de uso exibidos

---

**Recomendação:** Use **Render** (opção 1) - é a mais fácil!
