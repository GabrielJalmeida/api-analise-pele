@echo off
setlocal

cd /d "%~dp0"

echo [1/7] Verificando ferramentas...
where py >nul 2>&1 || goto :python_missing
where npm >nul 2>&1 || goto :node_missing
where rustc >nul 2>&1 || goto :rust_missing
where cargo >nul 2>&1 || goto :rust_missing

echo [2/7] Preparando ambiente de build da API...
if not exist .venv-build (
  py -3 -m venv .venv-build || goto :error
)
call .venv-build\Scripts\activate.bat || goto :error
python -m pip install --upgrade pip || goto :error
python -m pip install -r requirements-desktop.txt || goto :error

echo [3/7] Executando testes da API...
python -m pytest -q || goto :error

echo [4/7] Gerando API executavel...
python -m PyInstaller --noconfirm --clean desktop_api.spec || goto :error

echo [5/7] Preparando sidecar do Tauri...
for /f %%T in ('rustc --print host-tuple') do set "TARGET_TRIPLE=%%T"
if not defined TARGET_TRIPLE goto :error
if not exist admin\src-tauri\binaries mkdir admin\src-tauri\binaries
copy /Y "dist\lumina-api.exe" "admin\src-tauri\binaries\lumina-api-%TARGET_TRIPLE%.exe" >nul || goto :error

echo [6/7] Instalando dependencias do painel...
pushd admin
call npm ci || goto :admin_error
call npm run build || goto :admin_error

echo [7/7] Gerando instalador Windows...
cargo tauri --version >nul 2>&1
if errorlevel 1 cargo install tauri-cli --locked || goto :admin_error
cargo tauri build --bundles nsis || goto :admin_error
popd

echo.
echo Build concluido.
echo API independente: dist\lumina-api.exe
echo Instalador: admin\src-tauri\target\release\bundle\nsis\
exit /b 0

:admin_error
popd
goto :error

:python_missing
echo Python nao encontrado. Instale Python 3 e tente novamente.
exit /b 1

:node_missing
echo Node.js/npm nao encontrado. Instale a versao LTS e tente novamente.
exit /b 1

:rust_missing
echo Rust nao encontrado. Instale por https://rustup.rs e reinicie o terminal.
exit /b 1

:error
echo.
echo O build falhou. Revise a mensagem acima.
exit /b 1
