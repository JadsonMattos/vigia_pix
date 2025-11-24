document.addEventListener("DOMContentLoaded", () => {
    if (!window.realData) window.realData = [];
    renderTable();
    populateSelects();
    
    window.switchView = switchView;
    window.filterEmendas = filterEmendas;
    window.submitParliamentaryData = submitParliamentaryData;
    window.submitExecutorData = submitExecutorData;
    window.openDetail = openDetail;
    window.closeModal = closeModal;
});

function renderTable(data = window.realData) {
    const tbody = document.getElementById("emendasTableBody");
    tbody.innerHTML = "";

    data.forEach(item => {
        // Score Logic
        let scoreHtml = '<span style="color:#9CA3AF; font-size:0.8rem;">Pendente</span>';
        if (item.aiScore !== null) {
            const color = item.aiScore > 80 ? 'var(--color-success)' : 'var(--color-danger)';
            scoreHtml = `<strong style="color:${color}">${item.aiScore}/100</strong>`;
        }

        const tr = document.createElement("tr");
        tr.innerHTML = `
            <td>
                <span class="source-tag tag-portal">Portal</span><br>
                <strong>${item.id.split('-')[2]}-${item.id.split('-')[3]}</strong>
            </td>
            <td>${item.dep}<br><small style="color:#6B7280">${item.local}</small></td>
            <td><span class="badge" style="background:#DBEAFE; color:#1E40AF">${item.status_gov}</span></td>
            <td>${scoreHtml}</td>
            <td><button class="btn" style="padding:8px; border:1px solid #E5E7EB;" onclick="openDetail('${item.id}')"><i class="fa-solid fa-eye"></i></button></td>
        `;
        tbody.appendChild(tr);
    });
}

function switchView(viewName) {
    document.querySelectorAll(".view-section").forEach(el => el.classList.remove("active"));
    document.querySelectorAll(".nav-btn").forEach(el => el.classList.remove("active"));
    
    document.getElementById(`view-${viewName}`).classList.add("active");
    
    // Lógica simples para ativar o botão correto
    const idx = viewName === 'citizen' ? 0 : (viewName === 'parliamentary' ? 1 : 2);
    document.querySelectorAll(".nav-btn")[idx].classList.add("active");
}

function populateSelects() {
    const opts = window.realData.map(a => `<option value="${a.id}">${a.dep} - ${new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL', notation:"compact" }).format(a.valor_empenhado)}</option>`).join("");
    document.getElementById("parlaSelectEmenda").innerHTML = opts;
    document.getElementById("execSelectEmenda").innerHTML = opts;
}

function showLoading() { document.getElementById('loadingOverlay').style.display = 'flex'; }
function hideLoading() { document.getElementById('loadingOverlay').style.display = 'none'; }

// SUBMISSIONS
async function submitParliamentaryData() {
    const id = document.getElementById("parlaSelectEmenda").value;
    const obj = document.getElementById("parlaObjeto").value;
    const just = document.getElementById("parlaJustificativa").value;
    
    const idx = window.realData.findIndex(a => a.id === id);
    showLoading();
    
    window.realData[idx].parlaData = { objeto: obj, justificativa: just };
    
    // Chama IA
    const audit = await window.auditAmendment(window.realData[idx]);
    window.realData[idx].aiScore = audit.score;
    window.realData[idx].aiReason = audit.reason;
    
    hideLoading();
    renderTable();
    switchView('citizen');
    alert("Dados do Gabinete registrados!");
}

async function submitExecutorData() {
    const id = document.getElementById("execSelectEmenda").value;
    const prog = document.getElementById("execProgresso").value;
    const fotos = document.getElementById("execFotos").value;
    const rel = document.getElementById("execRelatorio").value;
    
    const idx = window.realData.findIndex(a => a.id === id);
    showLoading();
    
    window.realData[idx].executorData = { progresso: prog, fotos: fotos, relatorio: rel };
    
    const audit = await window.auditAmendment(window.realData[idx]);
    window.realData[idx].aiScore = audit.score;
    window.realData[idx].aiReason = audit.reason;
    
    hideLoading();
    renderTable();
    switchView('citizen');
    alert("Prestação de Contas enviada!");
}

// O MODAL CRUZADO
function openDetail(id) {
    const item = window.realData.find(a => a.id === id);
    const body = document.getElementById("modalBody");
    
    // Verifica quais dados existem
    const temParla = item.parlaData ? true : false;
    const temExec = item.executorData ? true : false;

    body.innerHTML = `
        <div style="background:#EFF6FF; padding:15px; border-radius:8px; margin-bottom:20px; border-left:4px solid var(--color-portal)">
            <strong style="color:var(--color-portal)">1. DADOS DO PORTAL (Automático)</strong>
            <div class="detail-grid" style="margin-top:10px;">
                <div><small>Valor:</small> <strong>${new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(item.valor_empenhado)}</strong></div>
                <div><small>Deputado:</small> <strong>${item.dep}</strong></div>
                <div><small>Local:</small> <strong>${item.local}</strong></div>
            </div>
        </div>

        <div style="background:${temParla ? '#F3E8FF' : '#F9FAFB'}; padding:15px; border-radius:8px; margin-bottom:20px; border-left:4px solid ${temParla ? 'var(--color-parla)' : '#9CA3AF'}">
            <strong style="color:${temParla ? 'var(--color-parla)' : '#9CA3AF'}">2. DADOS DO GABINETE (Enriquecimento)</strong>
            ${temParla ? `
                <div style="margin-top:10px;">
                    <small>Objeto Real:</small> <p>${item.parlaData.objeto}</p>
                    <small>Justificativa:</small> <p>${item.parlaData.justificativa}</p>
                </div>
            ` : '<p style="color:#9CA3AF; font-style:italic; font-size:0.9rem; margin-top:5px;">Aguardando input do parlamentar...</p>'}
        </div>

        <div style="background:${temExec ? '#FEF3C7' : '#F9FAFB'}; padding:15px; border-radius:8px; margin-bottom:20px; border-left:4px solid ${temExec ? 'var(--color-exec)' : '#9CA3AF'}">
            <strong style="color:${temExec ? 'var(--color-exec)' : '#9CA3AF'}">3. DADOS DO EXECUTOR (Prova de Vida)</strong>
            ${temExec ? `
                <div class="detail-grid" style="margin-top:10px;">
                    <div><small>Progresso:</small> <strong>${item.executorData.progresso}%</strong></div>
                    <div><small>Fotos:</small> <a href="#">Link Verificado</a></div>
                    <div style="grid-column: span 2"><small>Relatório:</small> <p>${item.executorData.relatorio}</p></div>
                </div>
            ` : '<p style="color:#9CA3AF; font-style:italic; font-size:0.9rem; margin-top:5px;">Aguardando prestação de contas...</p>'}
        </div>

        ${item.aiReason ? `
            <div style="background:#ECFDF5; padding:15px; border-radius:8px; border:1px solid var(--color-success);">
                <strong style="color:var(--color-success)"><i class="fa-solid fa-robot"></i> PARECER DA IA:</strong>
                <p style="margin-top:5px; font-size:0.9rem;">${item.aiReason}</p>
            </div>
        ` : ''}
    `;
    
    document.getElementById("detailModal").style.display = "flex";
}

function closeModal() { document.getElementById("detailModal").style.display = "none"; }
function filterEmendas() { renderTable(); } // Filtro simplificado para demo