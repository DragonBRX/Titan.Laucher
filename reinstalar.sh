#!/bin/bash

#=====================================================
# TITAN LAUNCHER - Script de Reinstalacao Automatica
#=====================================================

set -euo pipefail

# Cores
RED=\'\\033[0;31m\'
GREEN=\'\\033[0;32m\'
YELLOW=\'\\033[1;33m\'
BLUE=\'\\033[0;34m\'
CYAN=\'\\033[0;36m\'
BOLD=\'\\033[1m\'
NC=\'\\033[0m\'

# Configuracoes
APP_NAME="TitanLauncher"
INSTALL_DIR="$HOME/.local/share/$APP_NAME"
BIN_DIR="$HOME/.local/bin"
DESKTOP_DIR="$HOME/.local/share/applications"
ICON_DIR="$HOME/.local/share/icons/hicolor/256x256/apps"
CONFIG_DIR="$HOME/.config/titanlauncher"

# Logging
LOG_FILE="/tmp/titan-reinstall-$(date +%s).log"

log_info() {
    echo -e "${GREEN}[OK]${NC} $1" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[ERRO]${NC} $1" | tee -a "$LOG_FILE"
    exit 1
}

log_warn() {
    echo -e "${YELLOW}[AVISO]${NC} $1" | tee -a "$LOG_FILE"
}

log_step() {
    echo -e "${CYAN}[==>]${NC} ${BOLD}$1${NC}" | tee -a "$LOG_FILE"
}

# Banner
echo -e "${BLUE}${BOLD}"
cat << "EOF"
=============================================================
   _____ ___ _____ __    _____ _             _             
  |_   _|_ _|_   _/ _|  / ____| |           | |            
    | |  | |  | || |_  | |    | |_   _ _ __ | |_ __ _ _ __ 
    | |  | |  | ||  _| | |    | | | | | \'_ \| __/ _` | \'__|
   _| |_| || |_| || |   | |____| | |_| | |_) | || (_| | |   
  |_____|___|_____|_|    \_____|_|\__, | .__/ \__\__,_|_|   
                                   __/ | |                   
                                  |___/|_|                   
=============================================================
         UBUNTU/DEBIAN EDITION v3.0 - Reinstalador
=============================================================
EOF
echo -e "${NC}"

# Verificar se o usuario tem sudo
has_sudo() {
    if [ "$EUID" -eq 0 ]; then
        return 0
    fi
    sudo -n true 2>/dev/null
}

# Executar comando com sudo se necessario
run_sudo() {
    if [ "$EUID" -eq 0 ]; then
        "$@"
    else
        sudo "$@"
    fi
}

# ============================================================
# ETAPA 1: MATAR PROCESSOS E REMOVER INSTALACAO ANTERIOR
# ============================================================
log_step "Iniciando remocao da instalacao anterior..."

# Matar qualquer processo do titan-launcher rodando
if pgrep -f "titan-launcher" &>/dev/null; then
    log_warn "Titan Launcher esta em execucao. Fechando..."
    pkill -f "titan-launcher" 2>/dev/null || true
    sleep 2
fi

# Remover diretorios e arquivos da instalacao anterior
log_info "Removendo diretorios e arquivos de configuracao..."
rm -rf "$INSTALL_DIR" || true
rm -rf "$CONFIG_DIR" || true
rm -f "$BIN_DIR/titan-launcher" || true
rm -f "$DESKTOP_DIR/titan-launcher.desktop" || true
rm -f "$ICON_DIR/titan-launcher.png" || true

# Atualizar database de aplicativos
if command -v update-desktop-database &>/dev/null; then
    log_info "Atualizando database de aplicativos..."
    update-desktop-database "$DESKTOP_DIR" 2>/dev/null || true
fi

log_info "Remocao da instalacao anterior concluida."

# ============================================================
# ETAPA 2: ATUALIZAR REPOSITORIO GIT
# ============================================================
log_step "Atualizando repositorio Git..."

# Navegar para o diretorio do repositorio
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR" || log_error "Nao foi possivel navegar para o diretorio do script."

git pull || log_error "Falha ao atualizar o repositorio Git."

log_info "Repositorio Git atualizado com sucesso."

# ============================================================
# ETAPA 3: INSTALAR DEPENDENCIAS DO SISTEMA
# ============================================================
log_step "Verificando e instalando dependencias do sistema..."

if ! has_sudo; then
    log_error "Permissao sudo necessaria para instalar dependencias. Execute o script com sudo ou instale as dependencias manualmente: sudo apt update && sudo apt install -y python3 python3-pip python3-tk python3-venv openjdk-21-jre git"
fi

log_info "Atualizando lista de pacotes..."
run_sudo apt-get update -qq || log_error "Falha ao atualizar a lista de pacotes."

log_info "Instalando pacotes necessarios (python3, python3-pip, python3-tk, python3-venv, openjdk-21-jre, git)..."
run_sudo apt-get install -y -qq python3 python3-pip python3-tk python3-venv openjdk-21-jre git || log_error "Falha ao instalar dependencias do sistema."

log_info "Dependencias do sistema instaladas com sucesso."

# ============================================================
# ETAPA 4: EXECUTAR O SCRIPT DE INSTALACAO ORIGINAL
# ============================================================
log_step "Executando o script de instalacao original (install.sh)..."

# O install.sh pergunta "Deseja executar agora? [S/n]" no final. Responder 'S' automaticamente.
bash install.sh --run || log_error "Falha ao executar o script install.sh."

log_info "Script install.sh executado com sucesso."

log_step "Reinstalacao do Titan Launcher concluida com sucesso!"
log_info "Voce pode iniciar o Titan Launcher digitando 'titan-launcher' no terminal ou pelo menu de aplicativos."
