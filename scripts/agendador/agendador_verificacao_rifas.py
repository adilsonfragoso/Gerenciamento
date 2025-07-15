#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agendador Inteligente para Verificação de Rifas
Monitora rifas ativas com intervalos dinâmicos baseados em:
- Percentual de andamento (80% = 3min, 90% = 1min)
- Proximidade do horário de fechamento (15min antes = 1min)
- Intervalo padrão de 5 minutos

⚠️ IMPORTANTE: Antes de modificar este arquivo, leia a documentação em:
📖 scripts/agendador/README.md
🔗 scripts/agendador/DEPENDENCIAS.md

Este arquivo contém a lógica de negócio crítica do sistema de agendador.
É usado por agendador_servico.py e possui dependências complexas.
"""

import sys
import os
import time
import schedule
import threading
import logging
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import pymysql
from dotenv import load_dotenv

# Adicionar utils ao path para importar logging unificado
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils.logging_unificado import get_agendador_logger, log_system_info, log_system_shutdown

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

# Adicionar o diretório scripts ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importar o script de verificação existente
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from verificar_andamento_rifas import main as verificar_rifas
from recuperar_rifas_erro import main as recuperar_rifas_erro

# Importar configuração do banco
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from app.db_config import DB_CONFIG

# Configuração de logging unificado
logger = get_agendador_logger('AGENDADOR')

# ✅ Configuração do banco de dados (seguindo padrão MIGRACAO_ENV_CONSOLIDADO)
# DB_CONFIG é importado de app.db_config que já usa .env

# Horários de fechamento das extrações
HORARIOS_FECHAMENTO = {
    'PPT': '09:20',
    'PTM': '11:20', 
    'PT': '14:20',
    'PTV': '16:20',
    'PTN': '18:20',
    'FEDERAL': '19:00',
    'CORUJINHA': '21:30'
}

# Intervalos de monitoramento (em minutos)
INTERVALO_PADRAO = 5
INTERVALO_80_PERCENT = 3
INTERVALO_90_PERCENT = 1
INTERVALO_95_PERCENT_FOCO = 1  # Modo foco para rifas com 95%+
INTERVALO_PROXIMO_FECHAMENTO = 1
MINUTOS_ANTES_FECHAMENTO = 15

def notificar_dashboard_atualizado():
    """Notifica o dashboard que os dados foram atualizados"""
    try:
        # URL do endpoint no dashboard (assumindo que está rodando na porta 8001)
        dashboard_url = "http://localhost:8001/api/dashboard/notify-update"
        
        # Tentar notificar o dashboard
        response = requests.post(dashboard_url, timeout=3)
        
        if response.status_code == 200:
            logger.info("🔄 Dashboard notificado para atualização")
        else:
            logger.warning(f"⚠️ Dashboard respondeu com status {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        logger.debug("⚠️ Dashboard não está acessível - sem notificação")
    except requests.exceptions.Timeout:
        logger.warning("⚠️ Timeout ao notificar dashboard")
    except Exception as e:
        logger.warning(f"⚠️ Erro ao notificar dashboard: {e}")

def executar_envio_automatico_pdfs():
    """Executa o script de envio automático de PDFs para WhatsApp"""
    try:
        import subprocess
        import sys
        
        script_path = os.path.join(os.path.dirname(__file__), "envio_automatico_pdfs_whatsapp.py")
        
        if not os.path.exists(script_path):
            logger.debug("Script de envio automático de PDFs não encontrado")
            return
        
        logger.info("📄 Executando verificação de envio automático de PDFs...")
        
        # Executar o script
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            encoding='utf-8',
            timeout=180  # 3 minutos timeout para o agendador
        )
        
        if result.returncode == 0:
            # Log apenas se houver envios realizados
            output_lines = result.stdout.split('\n')
            envios_realizados = 0
            for line in output_lines:
                if 'PDFs enviados com sucesso:' in line:
                    try:
                        envios_realizados = int(line.split(':')[-1].strip())
                    except:
                        pass
            
            if envios_realizados > 0:
                logger.info(f"📱 {envios_realizados} PDF(s) enviado(s) automaticamente para WhatsApp")
            else:
                logger.debug("Nenhum PDF pendente para envio")
        else:
            logger.warning(f"Erro no script de envio automático: código {result.returncode}")
                
    except subprocess.TimeoutExpired:
        logger.warning("Timeout no script de envio automático de PDFs")
    except Exception as e:
        logger.debug(f"Erro ao executar envio automático: {e}")

class AgendadorRifas:
    def __init__(self):
        self.rifas_monitoradas = {}  # {sigla: {'percentual': int, 'proximo_check': datetime}}
        self.executando = False
        self.modo_foco_ativo = False  # Flag para modo foco
        self.rifa_em_foco = None  # Dados da rifa em foco (95%+)
        
    def extrair_sigla_base(self, sigla_oficial: str) -> str:
        """Extrai a sigla base (PPT, PTM, etc.) da sigla oficial"""
        sigla_upper = sigla_oficial.upper()
        
        # Verificar cada sigla base
        for sigla_base in HORARIOS_FECHAMENTO.keys():
            if sigla_upper.startswith(sigla_base):
                return sigla_base
                
        # Se não encontrou, retornar a primeira palavra
        return sigla_upper.split()[0] if sigla_upper else 'DESCONHECIDO'
    
    def calcular_proximo_fechamento(self, sigla_base: str) -> datetime:
        """Calcula o próximo horário de fechamento para uma sigla"""
        if sigla_base not in HORARIOS_FECHAMENTO:
            return None
            
        horario_str = HORARIOS_FECHAMENTO[sigla_base]
        hora, minuto = map(int, horario_str.split(':'))
        
        agora = datetime.now()
        fechamento_hoje = agora.replace(hour=hora, minute=minuto, second=0, microsecond=0)
        
        # Se já passou do horário de hoje, calcular para amanhã
        if agora > fechamento_hoje:
            fechamento_hoje += timedelta(days=1)
            
        return fechamento_hoje
    
    def esta_proximo_fechamento(self, sigla_base: str) -> bool:
        """Verifica se está próximo do horário de fechamento (15 min antes)"""
        fechamento = self.calcular_proximo_fechamento(sigla_base)
        if not fechamento:
            return False
            
        agora = datetime.now()
        tempo_restante = (fechamento - agora).total_seconds() / 60
        
        return 0 <= tempo_restante <= MINUTOS_ANTES_FECHAMENTO

    def verificar_modo_foco(self, rifas_ativas: List[Dict]) -> bool:
        """Verifica se alguma rifa atingiu 95% e ativa o modo foco"""
        # NOVA FUNCIONALIDADE: Verificar timeout do modo foco (máximo 3 horas)
        if self.modo_foco_ativo and self.rifa_em_foco:
            tempo_limite = datetime.now() - timedelta(hours=3)
            if hasattr(self, 'modo_foco_inicio') and self.modo_foco_inicio < tempo_limite:
                logger.warning(f"🕐 TIMEOUT DO MODO FOCO: {self.rifa_em_foco['sigla_oficial']} - Forçando saída")
                self.modo_foco_ativo = False
                self.rifa_em_foco = None
                delattr(self, 'modo_foco_inicio')
                return False
            
            # NOVA FUNCIONALIDADE: Verificar se passou do horário de fechamento
            sigla_base = self.extrair_sigla_base(self.rifa_em_foco['sigla_oficial'])
            if sigla_base in HORARIOS_FECHAMENTO:
                fechamento = self.calcular_proximo_fechamento(sigla_base)
                if fechamento and datetime.now() > fechamento:
                    logger.warning(f"⏰ HORÁRIO FECHAMENTO PASSOU: {self.rifa_em_foco['sigla_oficial']} - Forçando saída do modo foco")
                    self.modo_foco_ativo = False
                    self.rifa_em_foco = None
                    delattr(self, 'modo_foco_inicio')
                    return False
            
            # NOVA FUNCIONALIDADE: Verificar se está há muito tempo na mesma porcentagem (possível travamento)
            percentual_atual = self.rifa_em_foco.get('percentual', 0)
            agora = datetime.now()
            
            if hasattr(self, 'ultimo_percentual_foco') and hasattr(self, 'tempo_ultimo_percentual'):
                if (percentual_atual == self.ultimo_percentual_foco and 
                    (agora - self.tempo_ultimo_percentual).total_seconds() > 1800):  # 30 min sem mudança
                    logger.warning(f"⚠️ TRAVAMENTO DETECTADO: {self.rifa_em_foco['sigla_oficial']} há 30min em {percentual_atual}% - Forçando saída do modo foco")
                    self.modo_foco_ativo = False
                    self.rifa_em_foco = None
                    delattr(self, 'modo_foco_inicio')
                    delattr(self, 'ultimo_percentual_foco')
                    delattr(self, 'tempo_ultimo_percentual')
                    return False
            
            # Atualizar controle de percentual
            if not hasattr(self, 'ultimo_percentual_foco') or percentual_atual != self.ultimo_percentual_foco:
                self.ultimo_percentual_foco = percentual_atual
                self.tempo_ultimo_percentual = agora

        # Buscar rifas com 95%+ que não estão concluídas
        rifas_95_plus = [rifa for rifa in rifas_ativas if rifa['percentual'] >= 95 and rifa['status_rifa'] == 'ativo']

        if rifas_95_plus:
            # Se já estava em modo foco, verificar se a rifa ainda está ativa
            if self.modo_foco_ativo and self.rifa_em_foco:
                # Verificar se a rifa em foco ainda está na lista de 95%+
                rifa_atual_em_foco = next((r for r in rifas_95_plus if r['id'] == self.rifa_em_foco['id']), None)
                if rifa_atual_em_foco:
                    # Atualizar dados da rifa em foco
                    self.rifa_em_foco = rifa_atual_em_foco
                    logger.info(f"🎯 MODO FOCO MANTIDO: {self.rifa_em_foco['sigla_oficial']} ({self.rifa_em_foco['percentual']}%)")
                    return True
                else:
                    # Rifa em foco não está mais na lista (provavelmente concluída)
                    logger.info(f"🏆 RIFA EM FOCO CONCLUÍDA: {self.rifa_em_foco['sigla_oficial']} - SAINDO DO MODO FOCO")
                    self.modo_foco_ativo = False
                    self.rifa_em_foco = None

            # Se não estava em modo foco ou a rifa anterior foi concluída, ativar para a primeira rifa 95%+
            if not self.modo_foco_ativo:
                self.rifa_em_foco = rifas_95_plus[0]  # Pegar a primeira rifa com 95%+
                self.modo_foco_ativo = True
                self.modo_foco_inicio = datetime.now()  # NOVO: Registrar início do modo foco
                # NOVO: Inicializar controle de percentual
                self.ultimo_percentual_foco = self.rifa_em_foco.get('percentual', 0)
                self.tempo_ultimo_percentual = datetime.now()
                logger.info(f"🎯 MODO FOCO ATIVADO: {self.rifa_em_foco['sigla_oficial']} ({self.rifa_em_foco['percentual']}%)")
                logger.info("🔍 CONCENTRANDO MONITORAMENTO APENAS NESTA RIFA ATÉ 100%")
                logger.info(f"⏰ Timeout do modo foco: 3 horas máximo")
                logger.info(f"⚠️ Proteção anti-travamento: 30min na mesma porcentagem")
                return True
        else:
            # Nenhuma rifa com 95%+, desativar modo foco se estava ativo
            if self.modo_foco_ativo:
                logger.info(f"🔄 SAINDO DO MODO FOCO - Voltando ao monitoramento normal")
                self.modo_foco_ativo = False
                self.rifa_em_foco = None
                # Limpar atributos de controle
                if hasattr(self, 'modo_foco_inicio'):
                    delattr(self, 'modo_foco_inicio')
                if hasattr(self, 'ultimo_percentual_foco'):
                    delattr(self, 'ultimo_percentual_foco')
                if hasattr(self, 'tempo_ultimo_percentual'):
                    delattr(self, 'tempo_ultimo_percentual')
                if hasattr(self, 'modo_foco_inicio'):
                    delattr(self, 'modo_foco_inicio')

        return self.modo_foco_ativo

    def calcular_intervalo_monitoramento(self, percentual: int, sigla_base: str) -> int:
        """Calcula o intervalo de monitoramento baseado no percentual e proximidade do fechamento"""

        # Prioridade 1: Próximo do fechamento (15 min antes)
        if self.esta_proximo_fechamento(sigla_base):
            return INTERVALO_PROXIMO_FECHAMENTO

        # Prioridade 2: 95%+ de andamento (MODO FOCO)
        if percentual >= 95:
            return INTERVALO_95_PERCENT_FOCO

        # Prioridade 3: 90%+ de andamento
        if percentual >= 90:
            return INTERVALO_90_PERCENT
        elif percentual >= 80:
            return INTERVALO_80_PERCENT

        # Intervalo padrão
        return INTERVALO_PADRAO
    
    def buscar_rifas_ativas(self) -> List[Dict]:
        """Busca rifas ativas no banco de dados"""
        try:
            connection = pymysql.connect(**DB_CONFIG)
            cursor = connection.cursor()
            
            query = """
            SELECT id, edicao, sigla_oficial, andamento, status_rifa
            FROM extracoes_cadastro 
            WHERE status_rifa IN ('ativo', 'error')
            AND link IS NOT NULL 
            AND link != ''
            ORDER BY edicao DESC
            """
            
            cursor.execute(query)
            resultados = cursor.fetchall()
            
            rifas_ativas = []
            for resultado in resultados:
                # Extrair percentual numérico
                andamento_str = resultado[3] if resultado[3] else '0%'
                percentual = int(andamento_str.replace('%', '')) if andamento_str.replace('%', '').isdigit() else 0
                
                sigla_base = self.extrair_sigla_base(resultado[2])
                
                rifas_ativas.append({
                    'id': resultado[0],
                    'edicao': resultado[1],
                    'sigla_oficial': resultado[2],
                    'sigla_base': sigla_base,
                    'percentual': percentual,
                    'andamento_str': andamento_str,
                    'status_rifa': resultado[4]
                })
            
            cursor.close()
            connection.close()
            
            return rifas_ativas
            
        except Exception as e:
            logger.error(f"Erro ao buscar rifas ativas: {e}")
            return []
    
    def obter_rifas_ativas(self) -> List[Dict]:
        """Obtém lista de rifas ativas do banco de dados"""
        try:
            connection = pymysql.connect(**DB_CONFIG)
            cursor = connection.cursor()
            
            query = """
            SELECT id, edicao, sigla_oficial, andamento, status_rifa, data_sorteio
            FROM extracoes_cadastro
            WHERE status_rifa = 'ativo'
            AND link IS NOT NULL
            AND link != ''
            AND link LIKE 'https://litoraldasorte.com%'
            ORDER BY edicao DESC
            """
            
            cursor.execute(query)
            resultados = cursor.fetchall()
            
            rifas_ativas = []
            for resultado in resultados:
                # Extrair percentual do andamento
                andamento_str = resultado[3] if resultado[3] else '0%'
                percentual = 0
                if andamento_str and '%' in andamento_str:
                    try:
                        percentual = int(andamento_str.replace('%', ''))
                    except:
                        percentual = 0
                
                # Extrair sigla base
                sigla_base = self.extrair_sigla_base(resultado[2])
                
                rifas_ativas.append({
                    'id': resultado[0],
                    'edicao': resultado[1],
                    'sigla_oficial': resultado[2],
                    'andamento_str': andamento_str,
                    'percentual': percentual,
                    'status_rifa': resultado[4],
                    'data_sorteio': resultado[5],
                    'sigla_base': sigla_base
                })
            
            cursor.close()
            connection.close()
            
            return rifas_ativas
            
        except Exception as e:
            logger.error(f"Erro ao obter rifas ativas: {e}")
            return []

    def atualizar_cronograma_monitoramento(self):
        """Atualiza o cronograma de monitoramento baseado nas rifas ativas"""
        rifas_ativas = self.buscar_rifas_ativas()

        if not rifas_ativas:
            logger.info("Nenhuma rifa ativa encontrada")
            return

        logger.info(f"=== ATUALIZANDO CRONOGRAMA DE MONITORAMENTO ===")
        logger.info(f"Rifas ativas encontradas: {len(rifas_ativas)}")

        # NOVA FUNCIONALIDADE: Desativar rifas vencidas automaticamente
        self.desativar_rifas_vencidas(rifas_ativas)
        
        # Recarregar rifas ativas após possível desativação
        rifas_ativas = self.obter_rifas_ativas()
        if not rifas_ativas:
            logger.info("Nenhuma rifa ativa encontrada após verificação de vencimento")
            return

        # Verificar se deve ativar/manter modo foco
        modo_foco = self.verificar_modo_foco(rifas_ativas)

        # Limpar cronograma anterior
        schedule.clear()

        if modo_foco and self.rifa_em_foco:
            # MODO FOCO: Monitorar apenas a rifa com 95%+
            logger.info("🎯 MODO FOCO ATIVO - Monitorando apenas rifa crítica")
            rifas_para_monitorar = [self.rifa_em_foco]
            intervalo = INTERVALO_95_PERCENT_FOCO

            # Criar job específico para a rifa em foco
            self.criar_job_monitoramento(intervalo, rifas_para_monitorar)

            # Log específico do modo foco
            logger.info("📋 CRONOGRAMA MODO FOCO:")
            logger.info(f"🎯 A cada {intervalo} min (FOCO 95%+):")
            logger.info(f"  • {self.rifa_em_foco['sigla_oficial']} (Edição {self.rifa_em_foco['edicao']}) - {self.rifa_em_foco['andamento_str']}")

        else:
            # MODO NORMAL: Agrupar rifas por intervalo de monitoramento
            grupos_intervalo = {}

            for rifa in rifas_ativas:
                intervalo = self.calcular_intervalo_monitoramento(rifa['percentual'], rifa['sigla_base'])

                if intervalo not in grupos_intervalo:
                    grupos_intervalo[intervalo] = []
                grupos_intervalo[intervalo].append(rifa)

            # Criar jobs para cada grupo de intervalo
            for intervalo, rifas_grupo in grupos_intervalo.items():
                self.criar_job_monitoramento(intervalo, rifas_grupo)

            # Log do cronograma normal
            self.log_cronograma_atual(grupos_intervalo)
    
    def criar_job_monitoramento(self, intervalo: int, rifas: List[Dict]):
        """Cria um job de monitoramento para um grupo de rifas"""
        def executar_verificacao():
            if self.executando:
                logger.warning("Verificação já em execução, pulando...")
                return
                
            self.executando = True
            try:
                logger.info(f"🔄 Executando verificação (intervalo {intervalo}min)")
                rifas_info = []
                for r in rifas:
                    rifas_info.append(f"{r['sigla_oficial']} ({r['percentual']}%)")
                logger.info(f"Rifas a verificar: {rifas_info}")
                
                # Executar o script de verificação
                if self.modo_foco_ativo and self.rifa_em_foco:
                    # Modo foco: verificar apenas a rifa específica
                    logger.info(f"🎯 Verificando apenas rifa em foco: {self.rifa_em_foco['sigla_oficial']}")
                    try:
                        verificar_rifas([self.rifa_em_foco['id']])
                    except Exception as e:
                        logger.error(f"❌ ERRO NO MODO FOCO para {self.rifa_em_foco['sigla_oficial']}: {e}")
                        logger.warning("🔄 FORÇANDO SAÍDA DO MODO FOCO devido ao erro")
                        self.modo_foco_ativo = False
                        self.rifa_em_foco = None
                        if hasattr(self, 'modo_foco_inicio'):
                            delattr(self, 'modo_foco_inicio')
                        # Tentar verificação normal como fallback
                        logger.info("🔄 Tentando verificação normal como fallback...")
                        verificar_rifas()
                else:
                    # Modo normal: verificar todas as rifas ativas
                    verificar_rifas()
                
                # SEMPRE executar recuperação de rifas com erro após verificação
                logger.info("🔄 Verificando rifas com erro para recuperação...")
                recuperar_rifas_erro()
                
                # NOVA FUNCIONALIDADE: Notificar dashboard após verificação
                logger.info("📡 Notificando dashboard para atualização...")
                notificar_dashboard_atualizado()
                
                # NOVA FUNCIONALIDADE: Executar envio automático de PDFs se houver rifas concluídas
                logger.info("📄 Verificando envio automático de PDFs...")
                executar_envio_automatico_pdfs()
                
                # Reagendar baseado no novo estado
                self.atualizar_cronograma_monitoramento()
                
            except Exception as e:
                logger.error(f"Erro durante verificação: {e}")
            finally:
                self.executando = False
        
        # Agendar o job
        schedule.every(intervalo).minutes.do(executar_verificacao)
        logger.info(f"📅 Job criado: verificar a cada {intervalo} minutos")
    
    def log_cronograma_atual(self, grupos_intervalo: Dict):
        """Faz log do cronograma atual de monitoramento"""
        logger.info("📋 CRONOGRAMA ATUAL:")
        
        for intervalo, rifas in grupos_intervalo.items():
            motivo = self.obter_motivo_intervalo(intervalo, rifas)
            logger.info(f"⏰ Intervalo {intervalo}min ({motivo}):")
            
            for rifa in rifas:
                fechamento = self.calcular_proximo_fechamento(rifa['sigla_base'])
                tempo_restante = ""
                if fechamento:
                    minutos_restantes = (fechamento - datetime.now()).total_seconds() / 60
                    tempo_restante = f" | Fecha em {int(minutos_restantes)}min"
                
                logger.info(f"  • {rifa['sigla_oficial']} (Edição {rifa['edicao']}) - {rifa['andamento_str']}{tempo_restante}")
    
    def obter_motivo_intervalo(self, intervalo: int, rifas: List[Dict]) -> str:
        """Retorna o motivo do intervalo escolhido"""
        if intervalo == INTERVALO_PROXIMO_FECHAMENTO:
            return "próximo do fechamento"
        elif intervalo == INTERVALO_95_PERCENT_FOCO:
            return "FOCO 95%+ (modo concentrado)"
        elif intervalo == INTERVALO_90_PERCENT:
            return "90%+ de andamento"
        elif intervalo == INTERVALO_80_PERCENT:
            return "80%+ de andamento"
        else:
            return "intervalo padrão"
    
    def executar_verificacao_inicial(self):
        """Executa uma verificação inicial e configura o monitoramento"""
        logger.info("🚀 INICIANDO AGENDADOR INTELIGENTE DE RIFAS")
        logger.info("📊 Executando verificação inicial...")
        
        try:
            # Verificação inicial
            verificar_rifas()
            
            # Recuperar rifas com erro na inicialização
            logger.info("🔄 Verificando rifas com erro para recuperação...")
            recuperar_rifas_erro()
            
            # NOVA FUNCIONALIDADE: Notificar dashboard após verificação inicial
            logger.info("📡 Notificando dashboard para atualização inicial...")
            notificar_dashboard_atualizado()
            
            # Configurar monitoramento contínuo
            self.atualizar_cronograma_monitoramento()
            
            logger.info("✅ Agendador configurado com sucesso!")
            logger.info("🔄 Monitoramento contínuo iniciado...")
            
        except Exception as e:
            logger.error(f"Erro na verificação inicial: {e}")
    
    def executar_loop_principal(self):
        """Loop principal do agendador"""
        self.executar_verificacao_inicial()
        
        while True:
            try:
                schedule.run_pending()
                time.sleep(30)  # Verificar a cada 30 segundos
                
            except KeyboardInterrupt:
                logger.info("🛑 Agendador interrompido pelo usuário")
                break
            except Exception as e:
                logger.error(f"Erro no loop principal: {e}")
                time.sleep(60)  # Aguardar 1 minuto antes de tentar novamente

    def desativar_rifas_vencidas(self, rifas_ativas: List[Dict]):
        """Desativa automaticamente rifas que passaram 30min do horário de fechamento"""
        try:
            connection = pymysql.connect(**DB_CONFIG)
            cursor = connection.cursor()
            
            rifas_desativadas = 0
            agora = datetime.now()
            
            for rifa in rifas_ativas:
                sigla_base = rifa['sigla_base']
                
                if sigla_base in HORARIOS_FECHAMENTO:
                    fechamento = self.calcular_proximo_fechamento(sigla_base)
                    
                    if fechamento:
                        # Se passou 30 minutos do fechamento, desativar
                        limite_desativacao = fechamento + timedelta(minutes=30)
                        
                        if agora > limite_desativacao:
                            update_query = """
                            UPDATE extracoes_cadastro 
                            SET status_rifa = 'encerrado_automatico',
                                observacoes = CONCAT(IFNULL(observacoes, ''), 
                                    ' [AUTO-DESATIVADA: ', %s, ']')
                            WHERE id = %s
                            """
                            
                            timestamp = agora.strftime('%Y-%m-%d %H:%M')
                            cursor.execute(update_query, (timestamp, rifa['id']))
                            
                            logger.warning(f"🔄 RIFA AUTO-DESATIVADA: {rifa['sigla_oficial']} (passou 30min do fechamento)")
                            rifas_desativadas += 1
            
            if rifas_desativadas > 0:
                connection.commit()
                logger.info(f"✅ {rifas_desativadas} rifa(s) desativada(s) automaticamente")
            
            cursor.close()
            connection.close()
            
        except Exception as e:
            logger.error(f"Erro ao desativar rifas vencidas: {e}")

    def forcar_saida_modo_foco(self):
        """Força a saída do modo foco - útil para resolução manual de travamentos"""
        if self.modo_foco_ativo:
            logger.warning(f"🔧 FORÇANDO SAÍDA DO MODO FOCO: {self.rifa_em_foco['sigla_oficial'] if self.rifa_em_foco else 'N/A'}")
            self.modo_foco_ativo = False
            self.rifa_em_foco = None
            if hasattr(self, 'modo_foco_inicio'):
                delattr(self, 'modo_foco_inicio')
            
            # Limpar cronograma e reagendar modo normal
            schedule.clear()
            self.atualizar_cronograma_monitoramento()
            logger.info("✅ Modo foco desativado - voltando ao monitoramento normal")
            return True
        else:
            logger.info("ℹ️ Modo foco não estava ativo")
            return False

def main():
    """Função principal"""
    agendador = AgendadorRifas()
    agendador.executar_loop_principal()

if __name__ == "__main__":
    main()