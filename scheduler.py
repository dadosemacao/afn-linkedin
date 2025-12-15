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

# Configuração de logging básico (portável fora do Docker)
_log_file = os.getenv("SCHEDULER_LOG_FILE", "logs/scheduler.log")
try:
    Path(_log_file).parent.mkdir(parents=True, exist_ok=True)
except Exception:
    # Se não for possível criar diretório, segue apenas com stdout.
    _log_file = ""

_handlers = [logging.StreamHandler(sys.stdout)]
if _log_file:
    try:
        _handlers.append(logging.FileHandler(_log_file, encoding="utf-8"))
    except Exception:
        pass

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=_handlers
)
logger = logging.getLogger('scheduler')


class ApplicationScheduler:
    """Gerenciador de agendamento da aplicação."""
    
    def __init__(self):
        """Inicializa o scheduler."""
        self.schedule_enabled = os.getenv('SCHEDULE_ENABLED', 'true').lower() == 'true'
        self.schedule_cron = os.getenv('SCHEDULE_CRON', '0 8 * * 1,3,5')  # Seg/Qua/Sex às 08:00
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
            # Suporta lista (ex.: 1,3,5) e range (ex.: 1-5)
            day_names = []
            for token in weekday.split(','):
                token = token.strip()
                if not token:
                    continue
                if '-' in token:
                    start_s, end_s = token.split('-', 1)
                    try:
                        start = int(start_s)
                        end = int(end_s)
                    except ValueError:
                        day_names.append(f"dia {token}")
                        continue

                    for d in range(start, end + 1):
                        day_names.append(weekdays_map.get(str(d), f"dia {d}"))
                else:
                    day_names.append(weekdays_map.get(token, f"dia {token}"))

            if day_names:
                # Remove duplicatas preservando ordem
                seen = set()
                unique = []
                for n in day_names:
                    if n not in seen:
                        seen.add(n)
                        unique.append(n)
                description_parts.append("toda " + ", ".join(unique))
        
        if hour != '*' and minute != '*':
            description_parts.append(f"as {hour.zfill(2)}:{minute.zfill(2)}")
        elif hour != '*':
            description_parts.append(f"toda hora {hour}")
        
        return ' '.join(description_parts) if description_parts else "Execucao continua"

    @staticmethod
    def _cron_match(field: str, value: int) -> bool:
        """
        Verifica match de campo cron para um valor inteiro.
        Suporta '*', numero, lista 'a,b,c' e range 'a-b'.
        """
        field = (field or "").strip()
        if field == '*':
            return True

        for token in field.split(','):
            token = token.strip()
            if not token:
                continue
            if '-' in token:
                start_s, end_s = token.split('-', 1)
                try:
                    start = int(start_s)
                    end = int(end_s)
                except ValueError:
                    continue
                if start <= value <= end:
                    return True
            else:
                try:
                    if int(token) == value:
                        return True
                except ValueError:
                    continue

        return False

    @classmethod
    def _cron_match_weekday(cls, field: str, weekday_1_to_7: int) -> bool:
        """
        Match de dia-da-semana em cron.
        Aceita 0 ou 7 como Domingo. Internamente usamos 1..7 (Seg..Dom).
        """
        normalized = []
        for token in (field or "").split(','):
            token = token.strip()
            if not token:
                continue
            # Normaliza domingo 0 -> 7
            if token == "0":
                token = "7"
            if '-' in token:
                start_s, end_s = token.split('-', 1)
                if start_s == "0":
                    start_s = "7"
                if end_s == "0":
                    end_s = "7"
                normalized.append(f"{start_s}-{end_s}")
            else:
                normalized.append(token)

        return cls._cron_match(",".join(normalized) if normalized else field, weekday_1_to_7)
    
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
            self._cron_match(minute, now.minute),
            self._cron_match(hour, now.hour),
            self._cron_match(day, now.day),
            self._cron_match(month, now.month),
            self._cron_match_weekday(weekday, now.weekday() + 1),
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

