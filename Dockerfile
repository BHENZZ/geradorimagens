FROM python:3.11-slim

# Definir diretório de trabalho
WORKDIR /app

# Copiar arquivos de dependências
COPY requirements_imagens.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir gunicorn flask flask-cors

# Copiar código da aplicação
COPY . .

# Criar diretórios necessários
RUN mkdir -p static/imagens_geradas templates static/css static/js

# Expor porta
EXPOSE 8080

# Variável de ambiente para porta
ENV PORT=8080

# Comando para iniciar a aplicação
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 120 app:app
