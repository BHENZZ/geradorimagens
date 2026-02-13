// Variáveis globais
let currentDownloadUrl = '';

// Inicialização
document.addEventListener('DOMContentLoaded', function() {
    // Event Listeners
    const form = document.getElementById('formGerar');
    form.addEventListener('submit', gerarImagem);
    
    document.getElementById('btnRefreshGallery').addEventListener('click', carregarGaleria);
    
    // Upload de imagens
    setupImageUpload('imagem_produto', 'previewProduto');
    setupImageUpload('template', 'previewTemplate');
    
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

// Setup upload de imagem com preview
function setupImageUpload(inputId, previewId) {
    const input = document.getElementById(inputId);
    const preview = document.getElementById(previewId);
    const uploadArea = input.closest('.upload-area');
    
    input.addEventListener('change', function(e) {
        const file = e.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function(e) {
                preview.src = e.target.result;
                preview.style.display = 'block';
                uploadArea.querySelector('.upload-placeholder').style.display = 'none';
            };
            reader.readAsDataURL(file);
        }
    });
    
    // Drag and drop
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.style.borderColor = 'var(--primary-color)';
        uploadArea.style.background = 'var(--light-bg)';
    });
    
    uploadArea.addEventListener('dragleave', (e) => {
        e.preventDefault();
        uploadArea.style.borderColor = 'var(--border-color)';
        uploadArea.style.background = 'white';
    });
    
    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.style.borderColor = 'var(--border-color)';
        uploadArea.style.background = 'white';
        
        const file = e.dataTransfer.files[0];
        if (file && file.type.startsWith('image/')) {
            input.files = e.dataTransfer.files;
            const event = new Event('change');
            input.dispatchEvent(event);
        }
    });
}

// Função para gerar imagem
async function gerarImagem(e) {
    e.preventDefault();
    
    const btnGerar = document.getElementById('btnGerar');
    const resultsSection = document.getElementById('resultsSection');
    const resultsGrid = document.getElementById('resultsGrid');
    
    // Validação
    const imagemProduto = document.getElementById('imagem_produto').files[0];
    const fichaTecnica = document.getElementById('ficha_tecnica').value.trim();
    
    if (!imagemProduto) {
        alert('Por favor, envie a imagem do produto!');
        return;
    }
    
    if (!fichaTecnica) {
        alert('Por favor, preencha a ficha técnica do produto!');
        return;
    }
    
    // Desabilitar botão e mostrar loading
    btnGerar.disabled = true;
    btnGerar.querySelector('.btn-text').style.display = 'none';
    btnGerar.querySelector('.btn-loading').style.display = 'inline';
    
    // Mostrar seção de resultados com loading
    resultsSection.style.display = 'block';
    resultsGrid.innerHTML = '<div class="spinner"></div><p class="loading-text">Gerando suas imagens profissionais... Isso pode levar até 60 segundos.</p>';
    
    try {
        // Preparar FormData
        const formData = new FormData(document.getElementById('formGerar'));
        
        const response = await fetch('/gerar', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.sucesso) {
            // Mostrar imagens geradas
            mostrarResultados(data.imagens, data.prompt_usado);
            
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
                <small>Verifique sua conexão, a API Key e tente novamente.</small>
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
                <p><strong>Imagem ${index + 1}</strong></p>
                <button class="download-btn" onclick="downloadImagem('${img.url}', '${img.filename}')">
                    ⬇️ Download
                </button>
            </div>
        `;
        
        div.querySelector('img').addEventListener('click', function() {
            abrirModal(img.base64, `Imagem ${index + 1}`, img.url);
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
    // ESC para fechar modal
    if (e.key === 'Escape') {
        document.getElementById('imageModal').style.display = 'none';
    }
});
