"""Entrada da API local distribuída com o painel desktop.

O módulo configura o diretório persistente antes de importar a aplicação,
garantindo que SQLite, fotos e preferências nunca sejam gravados dentro da
pasta temporária criada pelo PyInstaller.
"""

from __future__ import annotations

import argparse
import ctypes
import logging
import os
import sys
import threading
import time

from pathlib import Path

import uvicorn
from dotenv import load_dotenv


def _argumentos():
    parser = argparse.ArgumentParser(
        description="API local do Skin Admin",
    )
    parser.add_argument("--data-dir")
    parser.add_argument("--parent-pid", type=int)
    parser.add_argument("--port", type=int, default=8765)
    return parser.parse_args()


def _diretorio_padrao() -> Path:
    if sys.platform == "win32":
        raiz = os.getenv("LOCALAPPDATA")
    else:
        raiz = os.getenv("XDG_DATA_HOME")

    if raiz:
        return Path(raiz) / "SkinAdmin"

    return Path.home() / ".skin-admin"


def _processo_ativo(pid: int) -> bool:
    if sys.platform == "win32":
        process_query = 0x1000
        still_active = 259
        kernel32 = ctypes.windll.kernel32
        handle = kernel32.OpenProcess(
            process_query,
            False,
            pid,
        )

        if not handle:
            return False

        codigo = ctypes.c_ulong()

        try:
            if not kernel32.GetExitCodeProcess(
                handle,
                ctypes.byref(codigo),
            ):
                return False

            return codigo.value == still_active
        finally:
            kernel32.CloseHandle(handle)

    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def _vigiar_processo_pai(pid: int):
    def vigiar():
        while _processo_ativo(pid):
            time.sleep(2)

        os._exit(0)

    threading.Thread(
        target=vigiar,
        name="parent-watchdog",
        daemon=True,
    ).start()


def main():
    argumentos = _argumentos()
    diretorio = Path(
        argumentos.data_dir
        or _diretorio_padrao()
    ).resolve()
    diretorio.mkdir(
        parents=True,
        exist_ok=True,
    )

    os.environ["LUMINA_DATA_DIR"] = str(diretorio)
    os.environ.setdefault("APP_ENV", "desktop")
    os.environ.setdefault(
        "CORS_ORIGINS",
        ",".join(
            [
                "http://tauri.localhost",
                "https://tauri.localhost",
                "tauri://localhost",
                "http://localhost:5173",
            ]
        ),
    )

    arquivo_configuracao = (
        diretorio / "config" / ".env"
    )
    load_dotenv(
        arquivo_configuracao,
        override=True,
    )

    logging.basicConfig(
        filename=diretorio / "lumina-api.log",
        level=logging.INFO,
        format=(
            "%(asctime)s %(levelname)s "
            "%(name)s %(message)s"
        ),
    )

    if argumentos.parent_pid:
        _vigiar_processo_pai(
            argumentos.parent_pid
        )

    # A importação acontece somente depois da configuração dos caminhos.
    from main import app

    uvicorn.run(
        app,
        host="127.0.0.1",
        port=argumentos.port,
        access_log=False,
        log_level="info",
    )


if __name__ == "__main__":
    main()
