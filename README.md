[README_WEB.md](https://github.com/user-attachments/files/25290821/README_WEB.md)
# 🎨 Gerador de Imagens AI - Google Gemini

Aplicação web completa para gerar imagens usando a API do Google Gemini Imagen 3.

![Python](https://img.shields.io/badge/Python-3.11-blue)
![Flask](https://img.shields.io/badge/Flask-3.0-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

## ✨ Características

- 🎨 Interface web moderna e responsiva
- 🖼️ Gera até 4 imagens por vez
- 📐 Múltiplas proporções (1:1, 16:9, 9:16, etc)
- 💾 Galeria automática de imagens geradas
- ⬇️ Download individual de imagens
- 📱 Totalmente responsivo (mobile-friendly)
- 🚀 Fácil de fazer deploy

## 🖥️ Demonstração

![Screenshot](screenshot.png)

## 📋 Pré-requisitos

- Python 3.8+
- Conta Google Cloud com API Gemini habilitada
- API Key do Google

## 🚀 Instalação Local

1. **Clone o repositório**
```bash
git clone https://github.com/seu-usuario/gerador-imagens-ai.git
cd gerador-imagens-ai
```

2. **Instale as dependências**
```bash
pip install -r requirements_imagens.txt
```

3. **Configure a API Key**
```bash
export GOOGLE_API_KEY="sua_chave_aqui"
```

Ou crie um arquivo `.env`:
```
GOOGLE_API_KEY=sua_chave_aqui
```

4. **Execute a aplicação**
```bash
python app.py
```

5. **Acesse no navegador**
```
http://localhost:5000
```

## 📁 Estrutura do Projeto

```
gerador-imagens-ai/
├── app.py                      # Aplicação Flask principal
├── templates/
│   └── index.html             # Interface HTML
├── static/
│   ├── css/
│   │   └── style.css          # Estilos
│   ├── js/
│   │   └── app.js             # JavaScript
│   └── imagens_geradas/       # Imagens salvas
├── requirements_imagens.txt   # Dependências Python
├── Procfile                   # Config Heroku/Render
├── Dockerfile                 # Config Docker
├── DEPLOY.md                  # Guia de deploy
└── README.md                  # Este arquivo
```

## 🌐 Deploy para Web

### Opção 1: Render (Recomendado)

1. Faça push para GitHub
2. Conecte no Render
3. Configure variável `GOOGLE_API_KEY`
4. Deploy automático!

[Guia completo de deploy →](DEPLOY.md)

### Opção 2: Docker

```bash
docker build -t gerador-imagens-ai .
docker run -p 8080:8080 -e GOOGLE_API_KEY=sua_chave gerador-imagens-ai
```

## 🎯 Como Usar

1. **Digite um prompt** descrevendo a imagem desejada
2. **Escolha o número de imagens** (1-4)
3. **Selecione a proporção** desejada
4. **Clique em "Gerar Imagem"**
5. **Aguarde** 10-30 segundos
6. **Baixe** as imagens geradas!

### 💡 Exemplos de Prompts

- `"um gato astronauta flutuando no espaço, arte digital, 8k"`
- `"paisagem cyberpunk futurista, neon, chuva, estilo blade runner"`
- `"retrato de mulher elegante, iluminação cinematográfica"`

## ⚙️ Configuração

### Variáveis de Ambiente

| Variável | Descrição | Obrigatório |
|----------|-----------|-------------|
| `GOOGLE_API_KEY` | Chave da API do Google | ✅ Sim |
| `PORT` | Porta da aplicação | ❌ Não (padrão: 5000) |

### Parâmetros da API

Editáveis em `app.py`:

```python
safety_filter_level="block_only_high"  # Nível de filtro
person_generation="allow_adult"        # Permitir pessoas
aspect_ratio="1:1"                     # Proporção
negative_prompt="ugly, blurry"         # O que evitar
```

## 💰 Custos

- **Hosting:** Grátis (tier inicial Render/Railway)
- **API Gemini:** ~$0.04 por imagem gerada
- **Quota Grátis:** Verifique em Google Cloud Console

## 🔐 Segurança

- ✅ API Key via variável de ambiente
- ✅ CORS configurado
- ✅ Validação de inputs
- ✅ Rate limiting (configurável)
- ⚠️ **NUNCA** comite a API Key no código!

## 🐛 Troubleshooting

### Erro: "API Key not valid"
- Verifique se a variável de ambiente está configurada
- Confirme que a API Vertex AI está ativada

### Erro: "Module not found"
- Execute: `pip install -r requirements_imagens.txt`

### Imagens não aparecem
- Verifique se a pasta `static/imagens_geradas/` existe
- Verifique permissões de escrita

## 🤝 Contribuindo

Contribuições são bem-vindas!

1. Fork o projeto
2. Crie uma branch: `git checkout -b feature/nova-feature`
3. Commit: `git commit -m 'Adiciona nova feature'`
4. Push: `git push origin feature/nova-feature`
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## 👤 Autor

Desenvolvido com ❤️ usando Google Gemini Imagen API

## 🙏 Agradecimentos

- Google Gemini Team
- Flask Framework
- Comunidade Open Source

## 📞 Suporte

- 📧 Email: seu@email.com
- 🐛 Issues: [GitHub Issues](https://github.com/seu-usuario/gerador-imagens-ai/issues)
- 📚 Docs: [DEPLOY.md](DEPLOY.md)

---

**⭐ Se este projeto foi útil, considere dar uma estrela!**
