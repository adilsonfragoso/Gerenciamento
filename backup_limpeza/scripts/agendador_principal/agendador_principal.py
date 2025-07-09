import schedule
import time
import os
from datetime import datetime, timedelta

def rodar_desativa_concluidas_v4():
    os.system("python scripts/desativa_concluidas_v4.py")

def rodar_alimenta_premiados():
    os.system("python scripts/alimenta_premiados.py")

# Mapear os dias da semana para facilitar o agendamento
DIA = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]

# Horários para cada caso
horarios_padrao = ["10:00", "11:00", "12:00", "15:00", "17:00", "19:00", "22:00"]   #sem federal
horarios_dias_federal = ["10:00", "11:00", "12:00", "15:00", "17:00", "19:30", "22:00"] #dias de federal
horarios_domingo = ["10:00", "11:00", "12:00", "15:00", "17:00"] #domingo

def horarios_menos_10min(lista_horarios):
    novos = []
    for h in lista_horarios:
        t = datetime.strptime(h, "%H:%M") - timedelta(minutes=10)
        novos.append(t.strftime("%H:%M"))
    return novos

for i, dia in enumerate(DIA):
    if dia == "wednesday" or dia == "saturday":
        for h in horarios_dias_federal:
            getattr(schedule.every(), dia).at(h).do(rodar_desativa_concluidas_v4)
        for h in horarios_menos_10min(horarios_dias_federal):
            getattr(schedule.every(), dia).at(h).do(rodar_alimenta_premiados)
    elif dia == "sunday":
        for h in horarios_domingo:
            getattr(schedule.every(), dia).at(h).do(rodar_desativa_concluidas_v4)
        for h in horarios_menos_10min(horarios_domingo):
            getattr(schedule.every(), dia).at(h).do(rodar_alimenta_premiados)
    else:
        for h in horarios_padrao:
            getattr(schedule.every(), dia).at(h).do(rodar_desativa_concluidas_v4)
        for h in horarios_menos_10min(horarios_padrao):
            getattr(schedule.every(), dia).at(h).do(rodar_alimenta_premiados)

while True:
    schedule.run_pending()
    time.sleep(1)
#quero criar uma documentação para o agendador

"""
Este script é um agendador de tarefas que utiliza a biblioteca 'schedule' para executar scripts Python em horários específicos.

Funções:
- rodar_desativa_concluidas_v4: Executa o script 'desativa_concluidas_v4.py'.
- rodar_alimenta_premiados: Executa o script 'alimenta_premiados.py'.

Mapeamento de dias da semana:
- Os dias da semana são mapeados para facilitar o agendamento das tarefas.

Horários:
- Existem horários padrão para a execução das tarefas, que variam dependendo do dia da semana.
- Para quartas e sábados, horários específicos são utilizados.
- Para domingos, um conjunto diferente de horários é aplicado.

Agendamento:
- As tarefas são agendadas utilizando a biblioteca 'schedule', que permite definir horários específicos para a execução das funções.
- O agendador roda em um loop infinito, verificando a cada segundo se há tarefas pendentes para serem executadas.

Dependências:
- Este script depende da biblioteca 'schedule' e deve ser executado em um ambiente onde essa biblioteca esteja instalada.
"""

