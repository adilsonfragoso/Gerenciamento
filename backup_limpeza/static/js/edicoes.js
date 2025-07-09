// ========================================
// EDICOES.JS - JavaScript da Página de Edições
// ========================================

// Variáveis globais
let modalDados = null;
let scriptDados = null;

// ========================================
// FUNÇÕES DE UTILIDADE
// ========================================

// Função para formatar data
function formatarData(dataString) {
    if (!dataString) return '-';
    
    try {
        // Criar data no fuso horário de São Paulo
        const data = new Date(dataString + 'T00:00:00-03:00'); // Fuso horário de São Paulo (UTC-3)
        const dia = String(data.getDate()).padStart(2, '0');
        const mes = String(data.getMonth() + 1).padStart(2, '0');
        const ano = String(data.getFullYear()).slice(-2); // Pega apenas os últimos 2 dígitos
        return `${dia}/${mes}/${ano}`;
    } catch (e) {
        return dataString;
    }
}

// Função para formatar dia da semana
function formatarDiaSemana(diaSemana) {
    if (!diaSemana) return '-';
    
    const dias = {
        'segunda': 'segunda',
        'segunda-feira': 'segunda',
        'terca': 'terça',
        'terça': 'terça',
        'terça-feira': 'terça',
        'quarta': 'quarta',
        'quarta-feira': 'quarta',
        'quinta': 'quinta',
        'quinta-feira': 'quinta',
        'sexta': 'sexta',
        'sexta-feira': 'sexta',
        'sabado': 'sábado',
        'sábado': 'sábado',
        'domingo': 'domingo'
    };
    
    return dias[diaSemana.toLowerCase()] || diaSemana;
}

// ========================================
// FUNÇÕES DE CARREGAMENTO DE DADOS
// ========================================

// Função para carregar edições
async function carregarEdicoes() {
    const loadingDiv = document.getElementById('loading');
    const errorDiv = document.getElementById('error');
    const noDataDiv = document.getElementById('no-data');
    const table = document.getElementById('edicoes-table');
    const tbody = document.getElementById('edicoes-tbody');
    
    try {
        loadingDiv.style.display = 'flex';
        errorDiv.style.display = 'none';
        noDataDiv.style.display = 'none';
        table.style.display = 'none';
        
        const response = await fetch('/api/edicoes');
        const edicoes = await response.json();
        
        loadingDiv.style.display = 'none';
        
        if (!edicoes || edicoes.length === 0) {
            noDataDiv.style.display = 'block';
            return;
        }
        
        // Limpar tabela
        tbody.innerHTML = '';
        
        // Processar cada edição e verificar pendências
        for (const edicao of edicoes) {
            console.log('Processando edição:', edicao);
            
            // Verificar pendências para este registro
            let temPendencias = false;
            try {
                const pendenciasResponse = await fetch(`/api/edicoes/${edicao.id}/tem-pendencias`);
                if (pendenciasResponse.ok) {
                    const pendenciasResult = await pendenciasResponse.json();
                    temPendencias = pendenciasResult.tem_pendencias;
                }
            } catch (error) {
                console.error('Erro ao verificar pendências para registro', edicao.id, ':', error);
            }
            
            const row = document.createElement('tr');
            
            // Adicionar ID do registro como atributo data
            row.setAttribute('data-id', edicao.id);
            // Adicionar data original como atributo data
            row.setAttribute('data-data-original', edicao.data_sorteio);
            
            // Log para verificar se os atributos foram definidos corretamente
            console.log('Atributos da linha:', {
                id: edicao.id,
                dataOriginal: edicao.data_sorteio,
                dataId: row.getAttribute('data-id'),
                dataDataOriginal: row.getAttribute('data-data-original'),
                temPendencias: temPendencias
            });
            
            // Verificar se a data é futura ou atual (permitir exclusão apenas dessas)
            const dataRegistro = new Date(edicao.data_sorteio + 'T00:00:00-03:00');
            const dataAtual = new Date();
            dataAtual.setHours(0, 0, 0, 0);
            const podeExcluir = dataRegistro >= dataAtual;
            
            // Adicionar classe para indicar que é clicável (apenas para datas futuras/atuais)
            if (podeExcluir) {
                row.classList.add('row-clicavel');
                row.title = 'Clique para excluir este registro';
            }
            
            // Célula combinada: dia da semana + data
            const sorteioCell = document.createElement('td');
            sorteioCell.className = 'dia-semana'; // Manter classe para compatibilidade
            sorteioCell.style.textAlign = 'center';
            sorteioCell.innerHTML = `
                <div style="font-weight: 500; color: #666;">${formatarDiaSemana(edicao.diaSemana)}</div>
                <div style="font-weight: 500; color: #1976d2;">${formatarData(edicao.data_sorteio)}</div>
            `;
            
            const siglasCell = document.createElement('td');
            siglasCell.className = 'siglas';
            siglasCell.style.textAlign = 'center';
            siglasCell.textContent = edicao.siglas || '-';
            
            const acoesCell = document.createElement('td');
            acoesCell.style.textAlign = 'center';
            
            if (temPendencias) {
                // Há pendências - mostrar botão
                const btnExecutar = document.createElement('button');
                btnExecutar.className = 'btn-executar-script';
                btnExecutar.textContent = '🚀 Executar Script';
                btnExecutar.title = `Executar cadRifas_litoral_latest para ${edicao.data_sorteio}`;
                btnExecutar.onclick = (e) => {
                    e.stopPropagation(); // Evitar que o clique propague para a linha
                    confirmarExecutarScript(edicao);
                };
                acoesCell.appendChild(btnExecutar);
            } else {
                // Não há pendências - mostrar texto informativo
                acoesCell.innerHTML = '<span style="color: #999; font-style: italic;">Sem pendências</span>';
            }
            
            row.appendChild(sorteioCell);
            row.appendChild(siglasCell);
            row.appendChild(acoesCell);
            
            tbody.appendChild(row);
        }
        
        table.style.display = 'table';
        
    } catch (error) {
        console.error('Erro ao carregar edições:', error);
        loadingDiv.style.display = 'none';
        errorDiv.style.display = 'block';
        errorDiv.querySelector('p').textContent = `Erro ao carregar as edições: ${error.message}`;
    }
}

// Função para carregar edições com problemas nos links
async function carregarEdicoesComProblemas() {
    try {
        const response = await fetch('/api/scripts/links-com-problemas');
        const data = await response.json();
        
        const listaElement = document.getElementById('listaEdicoesComProblemas');
        
        if (response.ok && data.success) {
            if (data.total === 0) {
                listaElement.textContent = 'Não há edições pendentes ou com erro';
                listaElement.style.color = '#6c757d';
            } else {
                // Separar edições por status
                const edicoesError = [];
                const edicoesPendente = [];
                
                data.edicoes_detalhadas.forEach(item => {
                    if (item.status_link === 'error') {
                        edicoesError.push(item.edicao);
                    } else if (item.status_link === 'pendente') {
                        edicoesPendente.push(item.edicao);
                    }
                });
                
                // Montar HTML com cores diferentes
                let html = '';
                if (edicoesError.length > 0) {
                    html += `<span style="color: #dc3545;">${edicoesError.join(' | ')}</span>`;
                }
                if (edicoesPendente.length > 0) {
                    if (html) html += ' | ';
                    html += `<span style="color: blue;">${edicoesPendente.join(' | ')}</span>`;
                }
                
                listaElement.innerHTML = html;
            }
        } else {
            listaElement.textContent = 'Erro ao carregar';
            listaElement.style.color = '#dc3545';
        }
    } catch (error) {
        console.error('Erro ao carregar edições com problemas:', error);
        document.getElementById('listaEdicoesComProblemas').textContent = 'Erro ao carregar';
        document.getElementById('listaEdicoesComProblemas').style.color = '#dc3545';
    }
}

// Função para carregar edições pendentes
async function carregarEdicoesPendentes() {
    try {
        const response = await fetch('/api/scripts/links-pendentes');
        const data = await response.json();
        
        const listaElement = document.getElementById('listaEdicoesPendentes');
        
        if (response.ok && data.success) {
            if (data.total === 0) {
                listaElement.textContent = 'Nenhuma edição pendente';
                listaElement.style.color = '#6c757d';
            } else {
                listaElement.textContent = data.edicoes.join(' | ');
                listaElement.style.color = 'blue';
            }
        } else {
            listaElement.textContent = 'Erro ao carregar';
            listaElement.style.color = '#dc3545';
        }
    } catch (error) {
        console.error('Erro ao carregar edições pendentes:', error);
        document.getElementById('listaEdicoesPendentes').textContent = 'Erro ao carregar';
        document.getElementById('listaEdicoesPendentes').style.color = '#dc3545';
    }
}

// Função para carregar a data padrão (próximo dia após o último sorteio)
async function carregarDataPadrao() {
    console.log('🚀 carregarDataPadrao iniciada');
    
    try {
        console.log('🌐 Fazendo requisição para /api/edicoes/ultima-data');
        const response = await fetch('/api/edicoes/ultima-data');
        console.log('📡 Resposta recebida:', response.status, response.statusText);
        
        if (!response.ok) {
            throw new Error(`Erro HTTP: ${response.status}`);
        }
        
        const data = await response.json();
        console.log('📦 Dados recebidos:', data);
        
        const novaDataInput = document.getElementById('novaData');
        if (!novaDataInput) {
            console.error('❌ Elemento novaData não encontrado!');
            return;
        }
        
        // Definir a data padrão (próximo dia após o último sorteio)
        novaDataInput.value = data.proxima_data;
        console.log('✅ Data padrão definida no input:', data.proxima_data);
        
        // Atualizar dia da semana e grupo
        console.log('🔄 Chamando atualizarDiaSemanaEGrupo com:', data.proxima_data);
        atualizarDiaSemanaEGrupo(data.proxima_data);
        
        console.log('✅ carregarDataPadrao concluída com sucesso');
        
    } catch (error) {
        console.error('❌ Erro ao carregar data padrão:', error);
        // Em caso de erro, usar data atual
        const hoje = new Date();
        const dataAtual = hoje.toISOString().split('T')[0];
        console.log('🔄 Usando data atual como fallback:', dataAtual);
        
        const novaDataInput = document.getElementById('novaData');
        if (novaDataInput) {
            novaDataInput.value = dataAtual;
            console.log('✅ Data atual definida no input:', dataAtual);
            atualizarDiaSemanaEGrupo(dataAtual);
        } else {
            console.error('❌ Elemento novaData não encontrado no fallback!');
        }
    }
}

// Função para carregar siglas por grupo
async function carregarSiglasPorGrupo(data) {
    console.log('🔍 carregarSiglasPorGrupo chamada com data:', data);
    
    try {
        const url = `/api/edicoes/siglas-por-grupo/${data}`;
        console.log('🌐 Fazendo requisição para:', url);
        
        const response = await fetch(url);
        console.log('📡 Resposta recebida:', response.status, response.statusText);
        
        if (!response.ok) {
            throw new Error(`Erro HTTP: ${response.status}`);
        }
        
        const resultado = await response.json();
        console.log('📦 Dados recebidos:', resultado);
        
        const dropdown = document.getElementById('siglasDropdown');
        if (!dropdown) {
            console.error('❌ Elemento siglasDropdown não encontrado!');
            return;
        }
        
        // Limpar dropdown
        dropdown.innerHTML = '<option value="">Selecione uma sigla...</option>';
        
        if (resultado.siglas && resultado.siglas.length > 0) {
            console.log('✅ Encontradas', resultado.siglas.length, 'siglas');
            resultado.siglas.forEach((registro, index) => {
                const option = document.createElement('option');
                option.value = JSON.stringify(registro);
                option.textContent = registro.siglas;
                dropdown.appendChild(option);
                console.log(`📝 Adicionada opção ${index + 1}:`, registro.siglas);
            });
        } else {
            console.log('⚠️ Nenhuma sigla encontrada');
            const option = document.createElement('option');
            option.value = "";
            option.textContent = "Nenhuma sigla encontrada";
            dropdown.appendChild(option);
        }
        
        console.log('✅ carregarSiglasPorGrupo concluída com sucesso');
        
    } catch (error) {
        console.error('❌ Erro ao carregar siglas:', error);
        const dropdown = document.getElementById('siglasDropdown');
        if (dropdown) {
            dropdown.innerHTML = '<option value="">Erro ao carregar siglas...</option>';
        }
    }
}

// Função para carregar premiações
async function carregarPremiacoes() {
    try {
        const response = await fetch('/api/premiacoes');
        if (!response.ok) {
            throw new Error(`Erro HTTP: ${response.status}`);
        }
        
        const premiacoes = await response.json();
        const dropdown = document.getElementById('premiacoesDropdown');
        
        // Limpar dropdown
        dropdown.innerHTML = '<option value="">Selecione uma sigla...</option>';
        
        if (premiacoes && premiacoes.length > 0) {
            premiacoes.forEach(premiacao => {
                const option = document.createElement('option');
                option.value = JSON.stringify(premiacao);
                option.textContent = premiacao.sigla; // Corrigido aqui
                dropdown.appendChild(option);
            });
        } else {
            const option = document.createElement('option');
            option.value = "";
            option.textContent = "Nenhuma sigla encontrada";
            dropdown.appendChild(option);
        }
        
    } catch (error) {
        console.error('Erro ao carregar siglas:', error);
        const dropdown = document.getElementById('premiacoesDropdown');
        dropdown.innerHTML = '<option value="">Erro ao carregar siglas...</option>';
    }
}

// ========================================
// FUNÇÕES DE ATUALIZAÇÃO DE INTERFACE
// ========================================

// Função para atualizar dia da semana e grupo baseado na data
function atualizarDiaSemanaEGrupo(dataString) {
    console.log('🔄 atualizarDiaSemanaEGrupo chamada com dataString:', dataString);
    
    if (!dataString) {
        console.warn('⚠️ dataString está vazia ou nula');
        return;
    }
    
    // Criar data no fuso horário de São Paulo
    const data = new Date(dataString + 'T00:00:00-03:00'); // Fuso horário de São Paulo (UTC-3)
    const diaSemana = data.getDay(); // 0=domingo, 1=segunda, ..., 6=sábado
    
    console.log('📅 Data criada:', data);
    console.log('📅 Dia da semana (número):', diaSemana);
    
    // Mapear número do dia para nome
    const diasSemana = ['domingo', 'segunda', 'terça', 'quarta', 'quinta', 'sexta', 'sábado'];
    const diaNome = diasSemana[diaSemana];
    
    // Determinar grupo
    let grupo;
    if (diaSemana === 0) { // domingo
        grupo = 3;
    } else if (diaSemana === 3 || diaSemana === 6) { // quarta ou sábado
        grupo = 2;
    } else { // segunda, terça, quinta, sexta
        grupo = 1;
    }
    
    console.log('📅 Dia nome:', diaNome);
    console.log('📅 Grupo:', grupo);
    
    // Atualizar displays
    const diaSemanaDisplay = document.getElementById('diaSemanaDisplay');
    if (diaSemanaDisplay) {
        diaSemanaDisplay.textContent = diaNome;
        console.log('✅ Display do dia da semana atualizado:', diaNome);
    } else {
        console.error('❌ Elemento diaSemanaDisplay não encontrado!');
    }
    
    // Carregar siglas do grupo
    console.log('🔄 Chamando carregarSiglasPorGrupo com:', dataString);
    carregarSiglasPorGrupo(dataString);
}

// ========================================
// FUNÇÕES DE MODAL
// ========================================

// Função para mostrar o modal de confirmação
function mostrarModalConfirmacao(dados, isSiglaAvulsa = false) {
    modalDados = dados;
    modalDados.isSiglaAvulsa = isSiglaAvulsa; // Adicionar flag para identificar sigla avulsa
    
    // Resetar estado do modal
    const editSection = document.getElementById('modalEditSection');
    const editInput = document.getElementById('modalEditInput');
    const btnEdit = document.getElementById('modalBtnEdit');
    const btnConfirm = document.getElementById('modalBtnConfirm');
    
    // Preencher informações no modal
    document.getElementById('modalData').textContent = dados.data_sorteio;
    document.getElementById('modalDia').textContent = dados.dia_semana;
    document.getElementById('modalSiglas').textContent = dados.siglas;
    
    // Resetar seção de edição
    editSection.style.display = 'none';
    editInput.value = '';
    
    // Resetar botões para estado inicial
    btnEdit.textContent = '✏️ Editar';
    btnEdit.disabled = false;
    btnConfirm.textContent = '✅ Confirmar';
    btnConfirm.style.background = '#28a745';
    btnConfirm.disabled = false;
    
    // Mostrar modal
    document.getElementById('modalOverlay').style.display = 'flex';
}

// Função para fechar o modal
function fecharModal() {
    document.getElementById('modalOverlay').style.display = 'none';
    
    // Resetar estado completamente
    const editSection = document.getElementById('modalEditSection');
    const editInput = document.getElementById('modalEditInput');
    const btnEdit = document.getElementById('modalBtnEdit');
    const btnConfirm = document.getElementById('modalBtnConfirm');
    
    editSection.style.display = 'none';
    editInput.value = '';
    btnEdit.textContent = '✏️ Editar';
    btnEdit.disabled = false;
    btnConfirm.textContent = '✅ Confirmar';
    btnConfirm.style.background = '#28a745';
    btnConfirm.disabled = false;
    
    modalDados = null;
}

// Função para alternar modo de edição
function alternarModoEdicao() {
    const editSection = document.getElementById('modalEditSection');
    const editInput = document.getElementById('modalEditInput');
    const btnEdit = document.getElementById('modalBtnEdit');
    const btnConfirm = document.getElementById('modalBtnConfirm');
    
    if (editSection.style.display === 'none') {
        // Entrar no modo edição
        editSection.style.display = 'block';
        editInput.value = modalDados.siglas;
        editInput.focus();
        btnEdit.textContent = '👁️ Visualizar';
        btnConfirm.textContent = '💾 Salvar e Confirmar';
        btnConfirm.style.background = '#17a2b8';
    } else {
        // Sair do modo edição
        editSection.style.display = 'none';
        btnEdit.textContent = '✏️ Editar';
        btnConfirm.textContent = '✅ Confirmar';
        btnConfirm.style.background = '#28a745';
    }
}

// Função para processar confirmação
async function processarConfirmacao() {
    const editSection = document.getElementById('modalEditSection');
    const editInput = document.getElementById('modalEditInput');
    const btnConfirm = document.getElementById('modalBtnConfirm');
    const btnEdit = document.getElementById('modalBtnEdit');
    
    // Determinar se está no modo edição
    const modoEdicao = editSection.style.display !== 'none';
    
    // Obter siglas (originais ou editadas)
    const siglasParaCadastrar = modoEdicao ? editInput.value.trim() : modalDados.siglas;
    
    // Validar siglas
    if (!siglasParaCadastrar) {
        alert('Por favor, insira pelo menos uma sigla.');
        return;
    }
    
    try {
        // Mostrar loading no botão
        const btnOriginalText = btnConfirm.textContent;
        btnConfirm.textContent = '⏳ Processando...';
        btnConfirm.disabled = true;
        btnEdit.disabled = true; // Desabilitar botão de editar também
        
        // Preparar dados para envio
        const dados = {
            data_sorteio: modalDados.data_sorteio,
            siglas: siglasParaCadastrar
        };
        
        // Determinar endpoint baseado no tipo de sigla
        let endpoint;
        if (modalDados.isSiglaAvulsa) {
            // Para sigla avulsa, usar endpoint específico
            endpoint = '/api/edicoes/cadastrar-sigla-avulsa';
            dados.dia_semana = modalDados.dia_semana;
        } else {
            // Para siglas normais, usar endpoint padrão
            endpoint = '/api/edicoes/cadastrar-siglas';
        }
        
        console.log('Dados para cadastro:', dados);
        console.log('Endpoint:', endpoint);
        
        // Fazer requisição para o backend
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(dados)
        });
        
        const resultado = await response.json();
        
        if (response.ok && resultado.success) {
            // Sucesso
            const tipoSigla = modalDados.isSiglaAvulsa ? 'Sigla avulsa' : 'Siglas';
            alert(`${tipoSigla} cadastrada(s) com sucesso!`);
            fecharModal();
            carregarEdicoes();
        } else {
            // Erro
            alert(`Erro ao cadastrar ${modalDados.isSiglaAvulsa ? 'sigla avulsa' : 'siglas'}: ${resultado.detail || resultado.message}`);
            fecharModal();
        }
    } catch (error) {
        console.error('Erro ao processar confirmação:', error);
        alert('Erro ao processar confirmação. Por favor, tente novamente mais tarde.');
        fecharModal();
    }
}

// ========================================
// FUNÇÕES DE EXCLUSÃO
// ========================================

// Função para excluir registro
async function excluirRegistro(id, dataOriginal, diaSemana) {
    console.log('Função excluirRegistro chamada com:', { id, dataOriginal, diaSemana });
    
    // Verificações adicionais
    if (!id || id === 'null' || id === 'undefined') {
        console.error('ID inválido na função excluirRegistro:', id);
        alert('Erro: ID do registro inválido. Não é possível excluir este registro.');
        return;
    }
    
    if (!dataOriginal) {
        console.error('Data original inválida na função excluirRegistro:', dataOriginal);
        alert('Erro: Data do registro inválida. Não é possível excluir este registro.');
        return;
    }
    
    try {
        console.log('Fazendo requisição DELETE para:', `/api/edicoes/excluir-siglas`);
        
        const response = await fetch(`/api/edicoes/excluir-siglas`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ id: parseInt(id) })
        });
        
        const resultado = await response.json();
        console.log('Resposta da exclusão:', resultado);
        
        if (response.ok && resultado.success) {
            alert(`Registro da data ${dataOriginal} (${diaSemana}) excluído com sucesso!`);
            carregarEdicoes(); // Recarregar a tabela
        } else {
            alert(`Erro ao excluir registro: ${resultado.detail || resultado.message}`);
        }
    } catch (error) {
        console.error('Erro ao excluir registro:', error);
        alert('Erro ao excluir registro. Por favor, tente novamente mais tarde.');
    }
}

// ========================================
// FUNÇÕES DE SCRIPTS
// ========================================

// Função para confirmar execução do script
async function confirmarExecutarScript(edicao) {
    console.log('confirmarExecutarScript chamada com edição:', edicao);
    
    try {
        // Primeiro, verificar se há pendências para este registro
        const response = await fetch(`/api/edicoes/${edicao.id}/tem-pendencias`);
        const resultado = await response.json();
        
        if (!response.ok) {
            throw new Error(resultado.detail || 'Erro ao verificar pendências');
        }
        
        if (!resultado.tem_pendencias) {
            alert('Não há edições pendentes para este registro.');
            return;
        }
        
        // Mostrar confirmação com detalhes das pendências
        const edicoesPendentes = resultado.edicoes_pendentes;
        const edicoesList = edicoesPendentes.map(e => `Edição ${e.edicao} (${e.sigla_oficial})`).join('\n');
        
        const confirmacao = confirm(
            `Executar script cadRifas_litoral_latest para:\n\n` +
            `Data: ${edicao.data_sorteio}\n` +
            `Siglas: ${edicao.siglas}\n\n` +
            `Edições pendentes (${resultado.total_pendencias}):\n${edicoesList}\n\n` +
            `Deseja continuar?`
        );
        
        if (!confirmacao) {
            return;
        }
        
        // Executar o script
        const scriptResponse = await fetch(`/api/scripts/executar-para-siglas/${edicao.id}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        const scriptResultado = await scriptResponse.json();
        
        if (scriptResponse.ok && scriptResultado.success) {
            alert(`✅ Script executado com sucesso!\n\n` +
                  `Edições processadas: ${scriptResultado.edicoes_processadas}\n` +
                  `Mensagem: ${scriptResultado.message}`);
            
            // Recarregar a lista de edições
            carregarEdicoes();
        } else {
            exibirErroScript(scriptResultado.detail || scriptResultado.message || 'Erro desconhecido ao executar script.');
        }
        
    } catch (error) {
        console.error('Erro ao executar script:', error);
        exibirErroScript(error.message || error);
    }
}

// Função para executar scripts
async function executarScript(tipo, botao, statusElementId, dadosAdicionais = {}) {
    const statusElement = document.getElementById(statusElementId);
    const textoOriginal = botao.textContent;
    
    try {
        // Mostrar loading
        botao.disabled = true;
        botao.textContent = '⏳ Executando...';
        statusElement.textContent = 'Executando script...';
        
        let response;
        
        // Usar endpoints corretos conforme documentação
        if (tipo === 'verificar-links') {
            response = await fetch('/api/scripts/verificar-links', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });
        } else if (tipo === 'enviar-pendentes') {
            response = await fetch('/api/scripts/enviar-links-pendentes', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });
        } else if (tipo === 'enviar-especificas') {
            response = await fetch('/api/scripts/enviar-edicoes-especificas', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(dadosAdicionais)
            });
        } else {
            throw new Error(`Tipo de script desconhecido: ${tipo}`);
        }
        
        const resultado = await response.json();
        
        if (response.ok && resultado.success) {
            statusElement.textContent = 'Script executado com sucesso!';
            statusElement.style.color = '#28a745';
            
            // Recarregar listas após execução dos scripts
            if (tipo === 'enviar-pendentes') {
                carregarEdicoesPendentes();
            } else if (tipo === 'verificar-links') {
                carregarEdicoesComProblemas();
            }
            
            // Atualizar logs com output detalhado do script
            const logsElement = document.getElementById('logsExecucao');
            const timestamp = new Date().toLocaleTimeString();
            
            // Adicionar mensagem de sucesso
            const logEntry = document.createElement('div');
            logEntry.innerHTML = `<span style="color: #28a745;">[${timestamp}]</span> ${tipo}: ${resultado.message || 'Executado com sucesso'}`;
            logsElement.appendChild(logEntry);
            
            // Adicionar output detalhado do script se disponível
            if (resultado.stdout) {
                const outputLines = resultado.stdout.split('\n');
                outputLines.forEach(line => {
                    if (line.trim()) {
                        const outputEntry = document.createElement('div');
                        outputEntry.innerHTML = `<span style="color: #6c757d; margin-left: 20px;">${line}</span>`;
                        logsElement.appendChild(outputEntry);
                    }
                });
            }
            
            // Adicionar erros se houver
            if (resultado.stderr) {
                const errorLines = resultado.stderr.split('\n');
                errorLines.forEach(line => {
                    if (line.trim()) {
                        const errorEntry = document.createElement('div');
                        errorEntry.innerHTML = `<span style="color: #dc3545; margin-left: 20px;">ERRO: ${line}</span>`;
                        logsElement.appendChild(errorEntry);
                    }
                });
            }
            
            logsElement.scrollTop = logsElement.scrollHeight;
            
        } else {
            statusElement.textContent = `Erro: ${resultado.detail || resultado.message}`;
            statusElement.style.color = '#dc3545';
            
            // Atualizar logs com erro
            const logsElement = document.getElementById('logsExecucao');
            const timestamp = new Date().toLocaleTimeString();
            const logEntry = document.createElement('div');
            logEntry.innerHTML = `<span style="color: #dc3545;">[${timestamp}]</span> ${tipo}: Erro - ${resultado.detail || resultado.message}`;
            logsElement.appendChild(logEntry);
            
            // Adicionar output de erro se disponível
            if (resultado.stdout) {
                const outputLines = resultado.stdout.split('\n');
                outputLines.forEach(line => {
                    if (line.trim()) {
                        const outputEntry = document.createElement('div');
                        outputEntry.innerHTML = `<span style="color: #6c757d; margin-left: 20px;">${line}</span>`;
                        logsElement.appendChild(outputEntry);
                    }
                });
            }
            
            if (resultado.stderr) {
                const errorLines = resultado.stderr.split('\n');
                errorLines.forEach(line => {
                    if (line.trim()) {
                        const errorEntry = document.createElement('div');
                        errorEntry.innerHTML = `<span style="color: #dc3545; margin-left: 20px;">${line}</span>`;
                        logsElement.appendChild(errorEntry);
                    }
                });
            }
            
            logsElement.scrollTop = logsElement.scrollHeight;
        }
        
    } catch (error) {
        console.error('Erro ao executar script:', error);
        statusElement.textContent = 'Erro ao executar script';
        statusElement.style.color = '#dc3545';
        
        // Atualizar logs com erro
        const logsElement = document.getElementById('logsExecucao');
        const timestamp = new Date().toLocaleTimeString();
        const logEntry = document.createElement('div');
        logEntry.innerHTML = `<span style="color: #dc3545;">[${timestamp}]</span> ${tipo}: Erro de conexão`;
        logsElement.appendChild(logEntry);
        logsElement.scrollTop = logsElement.scrollHeight;
        
    } finally {
        // Restaurar botão
        botao.disabled = false;
        botao.textContent = textoOriginal;
    }
}

// ========================================
// FUNÇÕES DE ERRO
// ========================================

function exibirErroScript(erro) {
    document.getElementById('erroScriptDetalhe').textContent = erro;
    document.getElementById('modalErroScript').style.display = 'flex';
}

function copiarErroScript() {
    const texto = document.getElementById('erroScriptDetalhe').textContent;
    navigator.clipboard.writeText(texto);
}

function fecharModalErroScript() {
    document.getElementById('modalErroScript').style.display = 'none';
}

// ========================================
// FUNÇÕES DE MENU MOBILE
// ========================================

// Função para toggle do menu mobile
function toggleMobileMenu() {
    const mobileNav = document.getElementById('mobileNav');
    mobileNav.classList.toggle('show');
}

// ========================================
// EVENT LISTENERS
// ========================================

// Inicialização quando o DOM estiver carregado
document.addEventListener('DOMContentLoaded', function() {
    // Carregar dados iniciais
    carregarEdicoes();
    carregarDataPadrao();
    carregarPremiacoes();
    carregarEdicoesPendentes();
    carregarEdicoesComProblemas();
    
    // Event listeners para o menu mobile
    const mobileMenuBtn = document.getElementById('mobileMenuBtn');
    const mobileNav = document.getElementById('mobileNav');
    const mobileLinks = document.querySelectorAll('.mobile-link');
    
    // Clique no botão hamburger
    mobileMenuBtn.addEventListener('click', toggleMobileMenu);
    
    // Fechar menu ao clicar em links
    mobileLinks.forEach(link => {
        link.addEventListener('click', () => {
            mobileNav.classList.remove('show');
        });
    });
    
    // Fechar menu ao redimensionar para desktop
    window.addEventListener('resize', () => {
        if (window.innerWidth > 768) {
            mobileNav.classList.remove('show');
        }
    });
    
    // Fechar menu ao clicar fora dele
    document.addEventListener('click', (e) => {
        if (!mobileMenuBtn.contains(e.target) && !mobileNav.contains(e.target)) {
            mobileNav.classList.remove('show');
        }
    });
    
    // Event listeners para os modais
    document.getElementById('modalBtnCancel').addEventListener('click', fecharModal);
    document.getElementById('modalBtnEdit').addEventListener('click', alternarModoEdicao);
    document.getElementById('modalBtnConfirm').addEventListener('click', processarConfirmacao);
    
    // Event listener para fechar modais clicando fora
    document.getElementById('modalOverlay').addEventListener('click', function(e) {
        if (e.target === this) {
            fecharModal();
        }
    });
    
    // Event listener para exclusão de linhas clicáveis
    document.addEventListener('click', function(e) {
        const row = e.target.closest('.row-clicavel');
        if (row) {
            e.preventDefault();
            e.stopPropagation();
            
            const id = row.getAttribute('data-id');
            const dataOriginal = row.getAttribute('data-data-original');
            const diaSemana = row.querySelector('.dia-semana').textContent;
            
            // Verificar se os dados estão válidos
            if (!id || id === 'null' || id === 'undefined') {
                console.error('ID inválido para exclusão:', id);
                alert('Erro: ID do registro inválido. Não é possível excluir este registro.');
                return;
            }
            
            if (!dataOriginal) {
                console.error('Data original inválida para exclusão:', dataOriginal);
                alert('Erro: Data do registro inválida. Não é possível excluir este registro.');
                return;
            }
            
            console.log('Tentando excluir registro:', { id, dataOriginal, diaSemana });
            
            if (confirm(`Deseja excluir o registro da data ${dataOriginal} (${diaSemana})?`)) {
                excluirRegistro(id, dataOriginal, diaSemana);
            }
        }
    });
    
    // Event listener para o botão Cadastrar Siglas
    document.getElementById('btnCadastrarSiglas').addEventListener('click', function() {
        const siglasDropdown = document.getElementById('siglasDropdown');
        const novaDataInput = document.getElementById('novaData');
        const diaSemanaDisplay = document.getElementById('diaSemanaDisplay');
        
        if (!siglasDropdown.value) {
            alert('Por favor, selecione uma opção de siglas primeiro.');
            return;
        }
        
        if (!novaDataInput.value) {
            alert('Por favor, selecione uma data primeiro.');
            return;
        }
        
        try {
            const siglasSelecionadas = JSON.parse(siglasDropdown.value);
            const dados = {
                data_sorteio: novaDataInput.value,
                dia_semana: diaSemanaDisplay.textContent,
                siglas: siglasSelecionadas.siglas
            };
            
            mostrarModalConfirmacao(dados);
        } catch (error) {
            console.error('Erro ao processar siglas selecionadas:', error);
            alert('Erro ao processar siglas selecionadas. Por favor, tente novamente.');
        }
    });
    
    // Event listener para o botão Cadastrar Sigla Avulsa
    document.getElementById('btnCadastrarSiglaAvulsa').addEventListener('click', function() {
        const premiacoesDropdown = document.getElementById('premiacoesDropdown');
        const novaDataInput = document.getElementById('novaData');
        const diaSemanaDisplay = document.getElementById('diaSemanaDisplay');
        
        if (!premiacoesDropdown.value) {
            alert('Por favor, selecione uma sigla primeiro.');
            return;
        }
        
        if (!novaDataInput.value) {
            alert('Por favor, selecione uma data primeiro.');
            return;
        }
        
        try {
            const premiaçãoSelecionada = JSON.parse(premiacoesDropdown.value);
            const siglaSelecionada = premiaçãoSelecionada.sigla;
            
            if (!confirm(`Deseja cadastrar a sigla avulsa "${siglaSelecionada}" para a data ${novaDataInput.value} (${diaSemanaDisplay.textContent})?`)) {
                return;
            }
            
            const dados = {
                data_sorteio: novaDataInput.value,
                dia_semana: diaSemanaDisplay.textContent,
                siglas: siglaSelecionada
            };
            
            mostrarModalConfirmacao(dados, true);
        } catch (error) {
            console.error('Erro ao processar sigla selecionada:', error);
            alert('Erro ao processar sigla selecionada. Por favor, tente novamente.');
        }
    });
    
    // Event listeners para os scripts
    document.getElementById('btnVerificarLinks').addEventListener('click', function() {
        executarScript('verificar-links', this, 'statusVerificarLinks');
    });
    
    document.getElementById('btnEnviarLinksPendentes').addEventListener('click', function() {
        executarScript('enviar-pendentes', this, 'statusEnviarPendentes');
    });
    
    document.getElementById('btnEnviarEdicoesEspecificas').addEventListener('click', function() {
        const input = document.getElementById('inputEdicoesEspecificas');
        const edicoesString = input.value.trim();
        
        if (!edicoesString) {
            alert('Por favor, insira os números das edições.');
            return;
        }
        
        // Converter string em array de números
        const edicoes = edicoesString.split(/\s+/).map(num => {
            const numero = parseInt(num.trim());
            if (isNaN(numero)) {
                throw new Error(`Edição inválida: ${num}`);
            }
            return numero;
        });
        
        if (edicoes.length === 0) {
            alert('Por favor, insira pelo menos uma edição válida.');
            return;
        }
        
        console.log('Enviando edições específicas:', edicoes);
        
        executarScript('enviar-especificas', this, 'statusEnviarEspecificas', { edicoes: edicoes });
    });
    
    // Event listener para limpar logs
    document.getElementById('btnLimparLogs').addEventListener('click', function() {
        document.getElementById('logsExecucao').innerHTML = '<div style="color: #6c757d; font-style: italic;">Aguardando execução de scripts...</div>';
    });
    
    // Event listener para mudança na data
    const novaDataInput = document.getElementById('novaData');
    novaDataInput.addEventListener('change', function() {
        atualizarDiaSemanaEGrupo(this.value);
    });
}); 