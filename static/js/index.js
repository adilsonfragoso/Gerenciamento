function carregarSiglas() {
    const tbody = document.querySelector('#siglas-table tbody');
    tbody.innerHTML = '<tr><td colspan="1" style="text-align: center;"><span id="spinner" style="display: inline-block; width: 20px; height: 20px; border: 2px solid #ccc; border-top: 2px solid #1976d2; border-radius: 50%; animation: spin 1s linear infinite;"></span> Carregando...</td></tr>';
    fetch('/siglas')
        .then(r => r.json())
        .then(siglas => {
            tbody.innerHTML = '';
            siglas.forEach(s => {
                const tr = document.createElement('tr');
                tr.innerHTML = `<td>${s.sigla}</td>`;
                tr.onclick = () => window.location.href = `/editar?id=${s.id}`;
                tbody.appendChild(tr);
            });
        })
        .catch (err => {
            tbody.innerHTML = '<tr><td colspan="1" style="text-align: center; color: red;"> Erro ao carregar dados. Tente novamente.</td></tr>';
            console.error("Erro ao carregar siglas:", err);
        });
}

function abrirFormularioNovo() {
    window.location.href = '/editar';
}

// Inicia o carregamento das siglas ao carregar a página.
document.addEventListener('DOMContentLoaded', carregarSiglas); 