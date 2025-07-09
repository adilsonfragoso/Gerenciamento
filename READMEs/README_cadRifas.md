# cadRifas_litoral_latest

> 📖 **Documentação Principal**: [README.md](README.md) - Visão geral completa do sistema

## Descrição

`cadRifas_litoral_latest` é o script oficial e testado para automação do cadastro de sorteios no sistema Litoral da Sorte, utilizando Selenium e integração direta com o banco de dados MySQL. Ele garante robustez, controle de edições, e segue todas as regras de negócio implementadas no backend.

---

## Objetivo
Automatizar o cadastro de sorteios a partir dos registros pendentes na tabela `extracoes_cadastro`, preenchendo todos os campos necessários, realizando upload de imagens e atualizando o status de cada edição cadastrada.

---

## Funcionamento
- O script busca todas as edições com `status_cadastro = 'pendente'` na tabela `extracoes_cadastro`.
- Processa as edições **da maior para a menor** (ordem decrescente de edição).
- Para cada edição:
  - Realiza login no sistema Litoral da Sorte.
  - Preenche todos os campos do sorteio conforme os dados do banco.
  - Faz upload da imagem correspondente (nome do arquivo igual ao campo `extracao`).
  - Clica no botão "Criar Sorteio" (modo produção) ou apenas simula (modo teste).
  - Atualiza o campo `status_cadastro` para `'cadastrado'` em caso de sucesso (apenas em produção).
- Gera logs detalhados de cada etapa.

---

## Parâmetros principais
- `CRIAR_SORTEIO = True`  
  - **True:** Executa o cadastro real no sistema e atualiza o status no banco.
  - **False:** Apenas simula o preenchimento, sem criar sorteio nem atualizar status (modo teste).
- Configurações de banco, login, pastas e timeout são centralizadas no arquivo `config_cadRifas.py`.

---

## Fluxo de uso
1. Certifique-se de que as edições pendentes estão corretamente cadastradas na tabela `extracoes_cadastro`.
2. Ajuste o parâmetro `CRIAR_SORTEIO` conforme desejado (produção ou teste).
3. Execute o script:
   ```sh
   python scripts/cadRifas_litoral_latest.py
   ```
4. Acompanhe os logs para verificar o andamento e possíveis erros.

---

## Dependências
- Python 3.8+
- Selenium
- mysql-connector-python
- ChromeDriver compatível com a versão do Google Chrome instalada
- Configuração correta do arquivo `config_cadRifas.py`

---

## Observações importantes
- O script **não gera links nem grava arquivos auxiliares**; toda a lógica de controle está centralizada no banco.
- O nome da imagem deve ser igual ao campo `extracao` da edição, com extensão `.jpeg` ou `.jpg`.
- O fluxo é robusto para execuções repetidas e concorrentes, evitando duplicidade de cadastros.
- O script foi extensivamente testado e é considerado a versão oficial para produção.

---

## Manutenção
- Para ajustes de regras de negócio, altere apenas o backend e a tabela `extracoes_cadastro`.
- Para novos campos ou mudanças de layout, atualize o script conforme necessário e revise este README.

---

## Funções do Script

### configurar_logging()
Configura o sistema de logging estruturado, criando arquivos de log e definindo o formato das mensagens. Retorna o logger principal utilizado em todo o script.

---

### validar_data(data_str: str) -> bool
Valida se uma string está no formato de data DD/MM/AAAA. Retorna True se válido, False caso contrário.

---

### validar_siglas(siglas: list) -> bool
Valida se uma lista de siglas está no formato correto (não vazia, strings com pelo menos 2 caracteres). Retorna True se todas as siglas forem válidas.

---

### exibir_siglas(siglas)
Exibe no log as siglas informadas para cadastro.

---

### esperar_elemento(driver, locator, cond=EC.visibility_of_element_located, to=None)
Aguarda até que um elemento esteja presente/visível/clicável na página, com timeout configurável. Utiliza as condições do Selenium.

---

### esperar_e_clicar(driver, locator, to=None)
Aguarda até que um elemento esteja clicável e executa o clique. Utiliza o timeout informado ou o padrão do sistema.

---

### fazer_login_e_abrir_navegador()
Abre o navegador, acessa o sistema Litoral da Sorte e realiza o login automaticamente. Retorna o driver Selenium autenticado.

---

### cadastrar_sorteio(driver, edicao_data)
Realiza todo o fluxo de cadastro de um sorteio, preenchendo campos, fazendo upload de imagem, prêmios, afiliados e pagamento. Utiliza os dados completos da edição vindos da tabela extracoes_cadastro.

---

### cadastrar_sorteio_com_retry(driver, edicao_data)
Executa o cadastro de sorteio com sistema de retry automático em caso de falha, conforme configuração. Garante robustez em situações de instabilidade.

---

### atualizar_status_cadastro(edicao)
Atualiza o campo status_cadastro para 'cadastrado' na tabela extracoes_cadastro para a edição informada, após cadastro bem-sucedido.

---

### ler_edicoes_pendentes_extracoes_cadastro()
Busca todas as edições pendentes (status_cadastro = 'pendente') na tabela extracoes_cadastro e retorna uma lista de dicts com todos os campos necessários para o cadastro.

---

### main()
Função principal do script. Valida configurações, busca edições pendentes, executa o fluxo de cadastro para cada edição (da maior para a menor), atualiza status e gera logs detalhados.

---

**Dúvidas ou sugestões:** consulte o responsável técnico ou abra uma issue no repositório do projeto. 