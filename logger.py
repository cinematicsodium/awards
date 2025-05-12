from datetime import datetime

from rich.console import Console

from constants import PathManager

console = Console()


class Logger:
    def _log(
        self,
        message: str = "",
        level: str = "INFO",
        color: str = "spring_green3",
        linebreak=True,
    ):
        padding = "\n" if linebreak is True else ""
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-4]
        
        console_msg = f"[{color}]{padding}{now} - {level}: {message}{padding}[/{color}]"
        file_msg = f"\n{padding}{now} - {level}: {message}{padding}"
        if level == "DASH":
            console_msg = f"[{color}]{padding}{'#'*100}{padding}[/{color}]"
            file_msg = f"\n{padding}{'#'*100}{padding}"
        console.print(console_msg)
        with open(PathManager.logger_path, "a", encoding="utf-8") as f:
            f.write(file_msg)

    def info(self, message):
        self._log(message, linebreak=False)

    def warning(self, message):
        self._log(message, "WARNING", "orange1")

    def error(self, message):
        self._log(message, "ERROR", "red1")

    def path(self, message):
        self._log(message)

    def final(self, message):
        _linebreak = "." * 50
        self._log(f"\n{message}\n{_linebreak}")
    
    def dash(self):
        self._log(level="DASH")
