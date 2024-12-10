from datetime import datetime


class SimpleLogger:
    def __init__(self, main_log='log main.log', info_log='log info.log', error_log='log error.log'):
        self.log_file = main_log
        self.info_log = info_log
        self.error_log = error_log

    def _log(self, level: str, message: str):
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-4]

        if level == 'INFO':
            with open(self.info_log, 'a') as f:
                f.write(f"\n{now} - {level}: {message}\n")
        elif level == 'ERROR':
            with open(self.error_log, 'a') as f:
                f.write(f"\n{now} - {level}: {message}\n")
        else:
            with open(self.log_file, 'a') as f:
                f.write(f"\n{now} - {level}: {message}\n")
        level = level + ':'
        print(f"{level.ljust(8)} {message}\n")

    def info(self, message):
        self._log('INFO', message)

    def warning(self, message):
        self._log('WARNING', message)

    def error(self, message):
        self._log('ERROR', message)
