// Variáveis globais
let currentDownloadUrl = '';

// Inicialização
document.addEventListener('DOMContentLoaded', function() {
    // Event Listeners
    document.getElementById('btnGerar').addEventListener('click', gerarImagem);
    document.getElementById('btnRefreshGallery').addEventListener('click', carregarGaleria);
    
    // Exemplos de prompts
    document.querySelectorAll('.example-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            document.getElementById('prompt').value = this.dataset.prompt;
        });
    });
    
    // Modal
    const modal = document.getElementById('imageModal');
    const modalClose = document.querySelector('.modal-close');
    const btnDownloadModal = document.getElementById('btnDownloadModal');
    
    modalClose.addEventListener('click', () => {
        modal.style.display = 'none';
    });
    
    window.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.style.display = 'none';
        }
    });
    
    btnDownloadModal.addEventListener('click', () => {
        if (currentDownloadUrl) {
            window.open(currentDownloadUrl, '_blank');
        }
    });
    
    // Carregar galeria inicial
    carregarGaleria();
});

// Função para gerar imagem
async function gerarImagem() {
    const prompt = document.getElementById('prompt').value.trim();
    const numImagens = parseInt(document.getElementById('num_imagens').value);
    const aspectRatio = document.getElementById('aspect_ratio').value;
    const btnGerar = document.getElementById('btnGerar');
    const resultsSection = document.getElementById('resultsSection');
    const resultsGrid = document.getElementById('resultsGrid');
    
    // Validação
    if (!prompt) {
        alert('Por favor, descreva a imagem que deseja gerar!');
        return;
    }
    
    // Desabilitar botão e mostrar loading
    btnGerar.disabled = true;
    btnGerar.querySelector('.btn-text').style.display = 'none';
    btnGerar.querySelector('.btn-loading').style.display = 'inline';
    
    // Mostrar seção de resultados com loading
    resultsSection.style.display = 'block';
    resultsGrid.innerHTML = '<div class="spinner"></div><p class="loading-text">Gerando suas imagens... Isso pode levar até 30 segundos.</p>';
    
    try {
        const response = await fetch('/gerar', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                prompt: prompt,
                num_imagens: numImagens,
                aspect_ratio: aspectRatio
            })
        });
        
        const data = await response.json();
        
        if (data.sucesso) {
            // Mostrar imagens geradas
            mostrarResultados(data.imagens, data.prompt);
            
            // Atualizar galeria
            setTimeout(() => carregarGaleria(), 1000);
            
            // Scroll suave para os resultados
            resultsSection.scrollIntoView({ behavior: 'smooth' });
        } else {
            throw new Error(data.erro || 'Erro ao gerar imagem');
        }
        
    } catch (error) {
        console.error('Erro:', error);
        resultsGrid.innerHTML = `
            <div style="text-align: center; padding: 40px; color: #ef4444;">
                <h3>❌ Erro ao gerar imagem</h3>
                <p>${error.message}</p>
                <small>Verifique sua conexão e a configuração da API Key.</small>
            </div>
        `;
    } finally {
        // Reabilitar botão
        btnGerar.disabled = false;
        btnGerar.querySelector('.btn-text').style.display = 'inline';
        btnGerar.querySelector('.btn-loading').style.display = 'none';
    }
}

// Função para mostrar resultados
function mostrarResultados(imagens, prompt) {
    const resultsGrid = document.getElementById('resultsGrid');
    resultsGrid.innerHTML = '';
    
    imagens.forEach((img, index) => {
        const div = document.createElement('div');
        div.className = 'result-item';
        div.innerHTML = `
            <img src="${img.base64}" alt="Imagem gerada ${index + 1}">
            <div class="result-item-overlay">
                <p><strong>Prompt:</strong> ${prompt}</p>
                <button class="download-btn" onclick="downloadImagem('${img.url}', '${img.filename}')">
                    ⬇️ Download
                </button>
            </div>
        `;
        
        div.querySelector('img').addEventListener('click', function() {
            abrirModal(img.base64, prompt, img.url);
        });
        
        resultsGrid.appendChild(div);
    });
}

// Função para carregar galeria
async function carregarGaleria() {
    const galleryGrid = document.getElementById('galleryGrid');
    galleryGrid.innerHTML = '<div class="spinner"></div><p class="loading-text">Carregando galeria...</p>';
    
    try {
        const response = await fetch('/galeria');
        const data = await response.json();
        
        if (data.sucesso) {
            if (data.imagens.length === 0) {
                galleryGrid.innerHTML = '<p class="loading-text">Nenhuma imagem gerada ainda. Crie sua primeira!</p>';
                return;
            }
            
            galleryGrid.innerHTML = '';
            data.imagens.forEach(img => {
                const div = document.createElement('div');
                div.className = 'gallery-item';
                div.innerHTML = `<img src="${img.url}" alt="${img.filename}">`;
                
                div.addEventListener('click', function() {
                    abrirModal(img.url, img.filename, img.url);
                });
                
                galleryGrid.appendChild(div);
            });
        } else {
            throw new Error(data.erro || 'Erro ao carregar galeria');
        }
        
    } catch (error) {
        console.error('Erro ao carregar galeria:', error);
        galleryGrid.innerHTML = '<p class="loading-text" style="color: #ef4444;">Erro ao carregar galeria</p>';
    }
}

// Função para abrir modal
function abrirModal(imageSrc, caption, downloadUrl) {
    const modal = document.getElementById('imageModal');
    const modalImg = document.getElementById('modalImage');
    const modalCaption = document.getElementById('modalCaption');
    
    modal.style.display = 'block';
    modalImg.src = imageSrc;
    modalCaption.textContent = caption;
    currentDownloadUrl = downloadUrl;
}

// Função para download de imagem
function downloadImagem(url, filename) {
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
}

// Atalhos de teclado
document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + Enter para gerar
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        document.getElementById('btnGerar').click();
    }
    
    // ESC para fechar modal
    if (e.key === 'Escape') {
        document.getElementById('imageModal').style.display = 'none';
    }
});
