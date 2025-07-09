# 📝 Sistema de Edição de Premiações - Upload de Imagens

**Data:** 21/06/2025  
**Status:** 📋 **DOCUMENTAÇÃO COMPLETA**

## 🎯 Visão Geral

O sistema de edição de premiações possui um campo específico para anexar imagens aos registros, com um fluxo bem estruturado de upload temporário e confirmação.

## 🔄 Fluxo de Funcionamento

### 1. 📂 Acesso à Edição
- **URL:** `/editar?id={premiacao_id}`
- **Arquivo:** `static/editar.html`
- **Comportamento:** Carrega automaticamente os dados da premiação, incluindo imagem existente

### 2. 🖼️ Campo de Seleção de Imagem

#### ✅ Características do Campo
- **Localização:** Após os campos de premiação, antes do botão "Salvar"
- **Formatos Aceitos:** Apenas JPG/JPEG
- **Tamanho Máximo:** 10MB
- **Métodos de Upload:**
  - 📁 Clique para selecionar arquivo
  - 🖱️ Drag & Drop (arrastar e soltar)

#### 🎨 Interface Visual
```html
<div class="image-upload-container">
    <input type="file" accept=".jpg,.jpeg" style="display: none;">
    <div id="uploadArea">
        <p>Clique aqui ou arraste uma imagem</p>
        <button>Selecionar Imagem</button>
        <div class="image-info">Formatos: JPG, JPEG. Máximo: 10MB</div>
    </div>
    <div id="imagePreview" style="display: none;">
        <img class="image-preview">
        <button class="remove-image">Remover Imagem</button>
    </div>
</div>
```

## 📋 Regras de Nomenclatura de Arquivos

### 🏷️ Padrão de Nomenclatura
**Regra Principal:** `{sigla_limpa}.jpg`

### 🧹 Processo de Limpeza da Sigla
```python
# Limpar a sigla para usar como nome do arquivo
sigla_limpa = "".join(c for c in sigla if c.isalnum() or c in (' ', '-', '_')).rstrip()
sigla_limpa = sigla_limpa.replace(' ', '_')

# Gerar nome final do arquivo
final_filename = f"{sigla_limpa}.jpg"
```

### 📝 Exemplos de Nomenclatura

| Sigla Original | Sigla Limpa | Nome do Arquivo |
|---------------|-------------|-----------------|
| `FEDERAL` | `FEDERAL` | `FEDERAL.jpg` |
| `PTM ESPECIAL` | `PTM_ESPECIAL` | `PTM_ESPECIAL.jpg` |
| `PT-40` | `PT-40` | `PT-40.jpg` |
| `CORUJINHA@#` | `CORUJINHA` | `CORUJINHA.jpg` |
| `PTV 16` | `PTV_16` | `PTV_16.jpg` |

## 🔄 Processo de Upload (2 Etapas)

### 📤 Etapa 1: Upload Temporário
**Endpoint:** `POST /upload-imagem-temp`

```javascript
// Quando usuário seleciona arquivo
async function handleImageFile(file) {
    // 1. Validações
    // 2. Preview temporário
    // 3. Upload para pasta temp
    const result = await uploadImageTemp(file);
    tempImagePath = result.temp_path; // Ex: "uploads/temp/temp_1703123456_a1b2c3d4.jpg"
}
```

**Resultado:**
- Arquivo salvo em `uploads/temp/` com nome único
- Preview mostrado ao usuário
- Caminho temporário armazenado em `tempImagePath`

### ✅ Etapa 2: Confirmação do Upload
**Endpoint:** `POST /confirmar-upload`

```javascript
// Quando usuário clica "Salvar"
if (tempImagePath) {
    const confirmResult = await confirmImageUpload(tempImagePath, sigla);
    uploadedImagePath = confirmResult.path; // Ex: "uploads/FEDERAL.jpg"
}
```

**Resultado:**
- Arquivo movido de `temp/` para `uploads/`
- Renomeado para `{sigla_limpa}.jpg`
- Arquivo antigo (se existir) é sobrescrito

## 🗂️ Estrutura de Diretórios

```
uploads/
├── temp/                           # Pasta para uploads temporários
│   ├── temp_1703123456_a1b2c3d4.jpg
│   └── temp_1703123789_e5f6g7h8.jpg
├── FEDERAL.jpg                     # Imagens confirmadas
├── PTM_ESPECIAL.jpg
├── PT-40.jpg
└── CORUJINHA.jpg
```

## 💾 Armazenamento no Banco de Dados

### 🗃️ Campo na Tabela
```sql
ALTER TABLE premiacoes 
ADD COLUMN imagem_path VARCHAR(255) NULL 
COMMENT 'Caminho relativo da imagem associada à premiação';
```

### 📊 Valores Armazenados
- **Com Imagem:** `"uploads/FEDERAL.jpg"`
- **Sem Imagem:** `NULL` ou `""`

## 🔧 Validações Implementadas

### ✅ Frontend (JavaScript)
```javascript
// Tipo de arquivo
if (!file.type.toLowerCase().includes('jpeg') && !file.type.toLowerCase().includes('jpg')) {
    alert('Por favor, selecione apenas arquivos JPG/JPEG.');
    return;
}

// Extensão do arquivo
if (!fileName.endsWith('.jpg') && !fileName.endsWith('.jpeg')) {
    alert('Por favor, selecione apenas arquivos com extensão .jpg ou .jpeg');
    return;
}

// Tamanho máximo
if (file.size > 10 * 1024 * 1024) {
    alert('Arquivo muito grande. Máximo 10MB.');
    return;
}
```

### ✅ Backend (Python)
```python
# Validar tipo de arquivo
if not file.content_type.lower() in ['image/jpeg', 'image/jpg']:
    raise HTTPException(status_code=400, detail="Apenas arquivos JPG/JPEG são permitidos")

# Validar extensão
file_extension = os.path.splitext(file.filename)[1].lower()
if file_extension not in ['.jpg', '.jpeg']:
    raise HTTPException(status_code=400, detail="Apenas arquivos com extensão .jpg ou .jpeg são permitidos")

# Validar tamanho
if file.size > 10 * 1024 * 1024:
    raise HTTPException(status_code=400, detail="Arquivo muito grande. Máximo 10MB")
```

## 🧹 Limpeza Automática

### 🗑️ Arquivos Temporários
- **Quando:** Usuário sai da página sem salvar
- **Como:** `beforeunload` event + `sendBeacon`
- **Endpoint:** `DELETE /remover-upload-temp`

### 🔄 Sobrescrita de Arquivos
- **Quando:** Nova imagem para sigla existente
- **Comportamento:** Arquivo antigo é automaticamente removido

## 📱 Responsividade

### 🖥️ Desktop
- Drag & Drop funcional
- Preview em tamanho normal
- Botões bem espaçados

### 📱 Mobile
- Touch-friendly
- Upload por toque
- Interface adaptada

## 🎯 Resumo do Comportamento

### ✅ Ao Abrir Edição
1. **Com imagem existente:** Mostra preview da imagem atual
2. **Sem imagem:** Mostra área de upload

### 📤 Ao Selecionar Nova Imagem
1. **Validações:** Tipo, extensão, tamanho
2. **Upload temporário:** Arquivo salvo em `temp/`
3. **Preview:** Imagem mostrada ao usuário
4. **Estado:** Aguardando confirmação

### 💾 Ao Salvar Formulário
1. **Se há imagem temporária:** Confirma upload (move para `uploads/`)
2. **Nomenclatura:** `{sigla_limpa}.jpg`
3. **Banco:** Caminho salvo em `imagem_path`
4. **Limpeza:** Arquivo temporário removido

### 🗑️ Ao Remover Imagem
1. **Frontend:** Remove preview e limpa variáveis
2. **Temporário:** Remove arquivo da pasta `temp/`
3. **Salvar:** Campo `imagem_path` fica vazio

## 🚀 Status Atual

- **Funcionalidade:** ✅ 100% Operacional
- **Validações:** ✅ Completas
- **Responsividade:** ✅ Total
- **Limpeza:** ✅ Automática
- **Performance:** ✅ Otimizada

**O sistema de upload de imagens está totalmente funcional e robusto!** 🎉 