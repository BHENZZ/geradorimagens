// ==========================================
// 🎨 MELIXPRESS AI - JavaScript
// ==========================================

document.addEventListener('DOMContentLoaded', function() {
    console.log('✅ MeliXpress AI carregado!');
    
    // Elementos
    const form = document.getElementById('formGerar');
    const btnGerar = document.getElementById('btnGerar');
    const btnText = document.getElementById('btnText');
    const btnLoading = document.getElementById('btnLoading');
    const resultados = document.getElementById('resultados');
    const imagensGeradas = document.getElementById('imagensGeradas');
    
    // Color pickers
    const corIcones = document.getElementById('cor_icones');
    const corIconesText = document.getElementById('cor_icones_text');
    const corFonte = document.getElementById('cor_fonte');
    const corFonteText = document.getElementById('cor_fonte_text');
    const corDestaque = document.getElementById('cor_destaque');
    const corDestaqueText = document.getElementById('cor_destaque_text');
    
    // Atualizar preview de cores
    if (corIcones) {
        corIcones.addEventListener('input', function(e) {
            corIconesText.value = e.target.value.toUpperCase();
        });
    }
    
    if (corFonte) {
        corFonte.addEventListener('input', function(e) {
            corFonteText.value = e.target.value.toUpperCase();
        });
    }
    
    if (corDestaque) {
        corDestaque.addEventListener('input', function(e) {
            corDestaqueText.value = e.target.value.toUpperCase();
        });
    }
    
    // Enviar formulário
    if (form) {
        form.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            console.log('📤 Enviando requisição...');
            
            // Mostrar loading
            btnGerar.disabled = true;
            btnText.style.display = 'none';
            btnLoading.style.display = 'flex';
            resultados.style.display = 'none';
            imagensGeradas.innerHTML = '';
            
            try {
                // Preparar dados
                const formData = new FormData();
                formData.append('ficha_tecnica', document.getElementById('ficha_tecnica').value);
                formData.append('fonte', document.getElementById('fonte').value);
                formData.append('cor_icones', document.getElementById('cor_icones').value);
                formData.append('cor_fonte', document.getElementById('cor_fonte').value);
                formData.append('cor_destaque', document.getElementById('cor_destaque').value);
                
                console.log('📝 Dados preparados:', {
                    ficha: document.getElementById('ficha_tecnica').value.substring(0, 50) + '...',
                    fonte: document.getElementById('fonte').value,
                    cores: {
                        icones: document.getElementById('cor_icones').value,
                        fonte: document.getElementById('cor_fonte').value,
                        destaque: document.getElementById('cor_destaque').value
                    }
                });
                
                // Enviar requisição
                const response = await fetch('/gerar', {
                    method: 'POST',
                    body: formData
                });
                
                console.log('📥 Resposta recebida:', response.status);
                
                // Verificar se response é JSON válido
                const contentType = response.headers.get('content-type');
                if (!contentType || !contentType.includes('application/json')) {
                    throw new Error('Resposta não é JSON válido. Verifique os logs do servidor.');
                }
                
                const data = await response.json();
                
                console.log('✅ Dados parseados:', data);
                
                if (data.sucesso) {
                    // Mostrar imagens
                    mostrarImagens(data.imagens);
                    
                    // Scroll para resultados
                    setTimeout(() => {
                        resultados.scrollIntoView({ behavior: 'smooth', block: 'start' });
                    }, 300);
                } else {
                    // Mostrar erro
                    mostrarErro(data.erro || 'Erro desconhecido');
                }
                
            } catch (error) {
                console.error('❌ Erro:', error);
                mostrarErro(`Erro: ${error.message}`);
            } finally {
                // Restaurar botão
                btnGerar.disabled = false;
                btnText.style.display = 'block';
                btnLoading.style.display = 'none';
            }
        });
    }
    
    // Função para mostrar imagens
    function mostrarImagens(imagens) {
        console.log(`🖼️ Mostrando ${imagens.length} imagens`);
        
        imagensGeradas.innerHTML = '';
        resultados.style.display = 'block';
        
        imagens.forEach((img, index) => {
            const card = document.createElement('div');
            card.className = 'result-card fade-in';
            card.style.animationDelay = `${index * 0.1}s`;
            
            card.innerHTML = `
                <img src="${img.base64}" alt="${img.tipo}">
                <h4>${img.tipo.replace(/_/g, ' ')}</h4>
                <p>${img.descricao}</p>
                <a href="${img.url}" download="${img.filename}" class="btn-primary" style="display: inline-block; padding: 12px 24px; text-decoration: none; font-size: 0.9rem;">
                    💾 Baixar Imagem
                </a>
            `;
            
            imagensGeradas.appendChild(card);
        });
    }
    
    // Função para mostrar erro
    function mostrarErro(mensagem) {
        console.error('🚨 Erro:', mensagem);
        
        imagensGeradas.innerHTML = `
            <div class="error-message" style="grid-column: 1 / -1;">
                <h3 style="margin-bottom: 10px;">❌ Erro ao gerar imagens</h3>
                <p>${mensagem}</p>
                <br>
                <p style="font-size: 0.9rem; opacity: 0.8;">
                    💡 <strong>Possíveis soluções:</strong><br>
                    • Verifique se a API Key está configurada corretamente no Render<br>
                    • Verifique se você tem quota disponível (500 imagens/dia grátis)<br>
                    • Tente novamente em alguns minutos
                </p>
            </div>
        `;
        resultados.style.display = 'block';
    }
});
