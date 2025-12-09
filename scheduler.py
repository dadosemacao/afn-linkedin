"""
Scheduler - Sistema de Agendamento Automático
==============================================
Gerencia a execução agendada da aplicação.
Executa toda segunda-feira às 08:00 (configurável).

Author: Sistema AFN
Date: 2025-12-09
Version: 2.0.0
"""

import os
import sys
import time
import signal
from datetime import datetime
from pathlib import Path
from typing import NoReturn
import subprocess
import logging

# Configuração de logging básico
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('/app/logs/scheduler.log')
    ]
)
logger = logging.getLogger('scheduler')


class ApplicationScheduler:
    """Gerenciador de agendamento da aplicação."""
    
    def __init__(self):
        """Inicializa o scheduler."""
        self.schedule_enabled = os.getenv('SCHEDULE_ENABLED', 'true').lower() == 'true'
        self.schedule_cron = os.getenv('SCHEDULE_CRON', '0 8 * * 1')  # Segunda-feira às 08:00
        self.running = True
        self.last_execution = None
        
        # Configuração de sinais para shutdown gracioso
        signal.signal(signal.SIGTERM, self._handle_signal)
        signal.signal(signal.SIGINT, self._handle_signal)
        
        logger.info("=" * 70)
        logger.info("Scheduler Inicializado")
        logger.info(f"Agendamento habilitado: {self.schedule_enabled}")
        logger.info(f"Expressao cron: {self.schedule_cron}")
        logger.info(f"Descricao: {self._describe_schedule()}")
        logger.info("=" * 70)
    
    def _handle_signal(self, signum, frame):
        """Trata sinais de encerramento."""
        logger.info(f"Sinal recebido: {signum}. Encerrando graciosamente...")
        self.running = False
    
    def _describe_schedule(self) -> str:
        """Descreve o agendamento em linguagem natural."""
        # Parse básico do cron (minuto hora dia mês dia-da-semana)
        parts = self.schedule_cron.split()
        
        if len(parts) != 5:
            return "Formato de cron invalido"
        
        minute, hour, day, month, weekday = parts
        
        # Mapeamento de dias da semana
        weekdays_map = {
            '0': 'Domingo',
            '1': 'Segunda-feira',
            '2': 'Terca-feira',
            '3': 'Quarta-feira',
            '4': 'Quinta-feira',
            '5': 'Sexta-feira',
            '6': 'Sabado',
            '7': 'Domingo'
        }
        
        description_parts = []
        
        if weekday != '*':
            day_name = weekdays_map.get(weekday, f"dia {weekday}")
            description_parts.append(f"toda {day_name}")
        
        if hour != '*' and minute != '*':
            description_parts.append(f"as {hour.zfill(2)}:{minute.zfill(2)}")
        elif hour != '*':
            description_parts.append(f"toda hora {hour}")
        
        return ' '.join(description_parts) if description_parts else "Execucao continua"
    
    def _should_execute_now(self) -> bool:
        """
        Verifica se deve executar agora baseado no cron.
        
        Returns:
            True se deve executar
        """
        now = datetime.now()
        minute, hour, day, month, weekday = self.schedule_cron.split()
        
        # Verifica cada componente do cron
        checks = [
            minute == '*' or int(minute) == now.minute,
            hour == '*' or int(hour) == now.hour,
            day == '*' or int(day) == now.day,
            month == '*' or int(month) == now.month,
            weekday == '*' or int(weekday) == now.weekday() + 1 or 
            (weekday == '0' and now.weekday() == 6)  # Domingo especial
        ]
        
        return all(checks)
    
    def _execute_application(self) -> bool:
        """
        Executa a aplicação principal.
        
        Returns:
            True se executou com sucesso
        """
        logger.info("=" * 70)
        logger.info(f"INICIANDO EXECUCAO AGENDADA - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("=" * 70)
        
        try:
            # Executa run.py
            result = subprocess.run(
                [sys.executable, '/app/run.py'],
                capture_output=True,
                text=True,
                timeout=3600  # Timeout de 1 hora
            )
            
            # Log do output
            if result.stdout:
                logger.info("STDOUT:")
                for line in result.stdout.split('\n'):
                    if line.strip():
                        logger.info(f"  {line}")
            
            if result.stderr:
                logger.warning("STDERR:")
                for line in result.stderr.split('\n'):
                    if line.strip():
                        logger.warning(f"  {line}")
            
            success = result.returncode == 0
            
            if success:
                logger.info("Execucao concluida com SUCESSO")
            else:
                logger.error(f"Execucao finalizada com codigo de erro: {result.returncode}")
            
            self.last_execution = datetime.now()
            
            logger.info("=" * 70)
            return success
            
        except subprocess.TimeoutExpired:
            logger.error("Execucao excedeu o tempo limite de 1 hora")
            return False
        
        except Exception as exc:
            logger.exception(f"Erro durante execucao: {exc}")
            return False
    
    def run(self) -> NoReturn:
        """Loop principal do scheduler."""
        logger.info("Scheduler em execucao. Aguardando momento de execucao...")
        
        if not self.schedule_enabled:
            logger.warning("Agendamento desabilitado. Executando uma vez e encerrando...")
            self._execute_application()
            return
        
        last_check_minute = -1
        
        while self.running:
            try:
                now = datetime.now()
                current_minute = now.minute
                
                # Verifica apenas uma vez por minuto
                if current_minute != last_check_minute:
                    last_check_minute = current_minute
                    
                    if self._should_execute_now():
                        # Evita execução duplicada no mesmo minuto
                        if (not self.last_execution or 
                            (now - self.last_execution).total_seconds() > 60):
                            self._execute_application()
                    else:
                        # Log de status a cada hora
                        if now.minute == 0:
                            next_desc = self._describe_schedule()
                            logger.info(
                                f"Status: Aguardando proxima execucao ({next_desc})"
                            )
                
                # Sleep por 30 segundos para reduzir uso de CPU
                time.sleep(30)
                
            except KeyboardInterrupt:
                logger.info("Interrupcao manual detectada")
                break
            
            except Exception as exc:
                logger.exception(f"Erro no loop do scheduler: {exc}")
                time.sleep(60)  # Wait 1 minuto antes de tentar novamente
        
        logger.info("Scheduler encerrado")


def main():
    """Função principal de entrada."""
    try:
        scheduler = ApplicationScheduler()
        scheduler.run()
        return 0
        
    except Exception as exc:
        logger.exception(f"Erro critico no scheduler: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())

