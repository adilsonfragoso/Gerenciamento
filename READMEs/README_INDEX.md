# 📚 Índice de Documentação - Sistema de Gerenciamento de Sorteios

> 🎯 **Documentação Principal**: [README.md](README.md) - Visão geral completa do sistema

## 📋 Estrutura da Documentação

### **📖 Documentação Principal**
- **[README.md](README.md)** - Documentação centralizada e completa do sistema
  - Visão geral, funcionalidades, endpoints, scripts, interface
  - Troubleshooting, configuração, fluxos de trabalho
  - **Recomendado como primeiro contato com o sistema**

### **🔧 Documentação Específica por Funcionalidade**

#### **Cadastro e Gerenciamento**
- **[README_CadastrarSiglas.md](README_CadastrarSiglas.md)** - Botão "Cadastrar Siglas" e "Cadastrar Sigla Avulsa"
  - Fluxo completo, modais, validações, tratamento de erros
  - Campo `id_siglas_diarias` e rastreabilidade
  - **Exclusão direta de siglas cadastradas pela tabela** (com confirmação e exclusão em cascata)
  - **Para desenvolvedores que trabalham com cadastro**

- **[README_EDICOES.md](README_EDICOES.md)** - Módulo completo de edições
  - Endpoints da API, frontend, JavaScript, regras de negócio
  - Lógica de grupos, status de pendências, modais
  - **Exclusão de registros de siglas diretamente pela tabela**
  - **Para desenvolvedores backend e frontend**

#### **Scripts de Automação**
- **[README_cadRifas.md](README_cadRifas.md)** - Script de automação Litoral da Sorte
  - Configurações, funções, parâmetros, manutenção
  - Modos teste e produção, tratamento de erros
  - **Para desenvolvedores de automação**

- **[READMEs/README_novo_chamadas_group_latest.md](READMEs/README_novo_chamadas_group_latest.md)** - Script de envio WhatsApp
  - Duas lógicas de envio (pendentes e específicas)
  - Configurações, exemplos de uso, troubleshooting
  - **Para desenvolvedores de integração**

#### **Planejamento e Desenvolvimento**
- **[READMEs/PRÓXIMOS_PASSOS.md](READMEs/PRÓXIMOS_PASSOS.md)** - Roadmap e próximas implementações
  - Estado atual, prioridades, considerações técnicas
  - Processo diário atual vs. futuro
  - **Para equipe de desenvolvimento e gestão**

## 🎯 Como Usar a Documentação

### **Para Novos Desenvolvedores**
1. **Comece pelo [README.md](README.md)** - Entenda o sistema
2. **Consulte READMEs específicos** conforme necessidade
3. **Use este índice** para navegar rapidamente

### **Para Usuários Finais**
1. **Leia apenas o [README.md](README.md)** - Cobre todas as funcionalidades
2. **Consulte troubleshooting** quando necessário

### **Para Manutenção**
1. **README.md** para mudanças gerais
2. **READMEs específicos** para mudanças pontuais
3. **Atualize referências cruzadas** quando necessário

## 🔗 Referências Cruzadas

### **Navegação Bidirecional**
- Todos os READMEs específicos têm referência para o README principal
- README principal tem referências para todos os READMEs específicos
- Este índice serve como ponto central de navegação

### **Organização por Categoria**
- **Funcionalidades**: Cadastro e gerenciamento
- **Automação**: Scripts e integrações
- **Planejamento**: Roadmap e desenvolvimento

## 📝 Recomendações de Uso

### **Para Desenvolvedores**
- **Primeira leitura**: [README.md](README.md)
- **Funcionalidade específica**: README correspondente
- **Manutenção**: README específico + README principal

### **Para Usuários**
- **Uso diário**: [README.md](README.md)
- **Problemas**: Seção troubleshooting do README principal
- **Funcionalidades avançadas**: READMEs específicos

### **Para Gestão**
- **Visão geral**: [README.md](README.md)
- **Planejamento**: [READMEs/PRÓXIMOS_PASSOS.md](READMEs/PRÓXIMOS_PASSOS.md)
- **Status atual**: Seção "Estado Atual" dos READMEs

## 🔄 Atualizações

### **Quando Atualizar**
- **README.md**: Mudanças gerais no sistema
- **READMEs específicos**: Mudanças em funcionalidades específicas
- **Este índice**: Adição de novos documentos ou reorganização

### **Como Atualizar**
1. Atualize o documento específico
2. Atualize referências cruzadas
3. Atualize este índice se necessário
4. Verifique consistência entre documentos

---

**Última Atualização**: Janeiro 2025  
**Versão**: 2.0.0  
**Status**: Estrutura completa com referências cruzadas 