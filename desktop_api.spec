from PyInstaller.utils.hooks import collect_data_files, collect_submodules


hiddenimports = []
datas = []


def modulo_de_execucao(nome):
    partes = nome.split(".")

    if any(
        parte in {"test", "tests"}
        or parte.startswith("test_")
        or parte.startswith("_test")
        for parte in partes
    ):
        return False

    opcionais_nao_usados = (
        "google.genai.local_tokenizer",
        "google.genai._local_tokenizer_loader",
        "openai.helpers",
        "openai._extras",
    )

    return not nome.startswith(
        opcionais_nao_usados
    )


for pacote in (
    "google.genai",
    "openai",
    "anthropic",
):
    hiddenimports += collect_submodules(
        pacote,
        filter=modulo_de_execucao,
        on_error="ignore",
    )
    datas += collect_data_files(
        pacote,
        excludes=[
            "**/test/**",
            "**/tests/**",
        ],
    )


a = Analysis(
    ["desktop_api.py"],
    pathex=["."],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        "tkinter",
        "matplotlib",
        "numpy",
        "pytest",
        "_pytest",
    ],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="lumina-api",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
)
