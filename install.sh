#!/bin/bash
#=====================================================
# TITAN LAUNCHER - UBUNTU/DEBIAN EDITION
# Script de Instalacao Automatica Otimizado
#=====================================================

set -euo pipefail

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

# Configuracoes
APP_NAME="TitanLauncher"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALL_DIR="$HOME/.local/share/$APP_NAME"
BIN_DIR="$HOME/.local/bin"
DESKTOP_DIR="$HOME/.local/share/applications"
ICON_DIR="$HOME/.local/share/icons/hicolor/256x256/apps"
CONFIG_DIR="$HOME/.config/titanlauncher"

# Logging
LOG_FILE="/tmp/titan-install-$(date +%s).log"

log_info() {
    echo -e "${GREEN}[OK]${NC} $1" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[ERRO]${NC} $1" | tee -a "$LOG_FILE"
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
    | |  | |  | ||  _| | |    | | | | | '_ \| __/ _` | '__|
   _| |_| || |_| || |   | |____| | |_| | |_) | || (_| | |   
  |_____|___|_____|_|    \_____|_|\__, | .__/ \__\__,_|_|   
                                   __/ | |                   
                                  |___/|_|                   
=============================================================
         UBUNTU/DEBIAN EDITION - Instalador
=============================================================
EOF
echo -e "${NC}"

# ============================================================
# FUNCOES DE UTILIDADE
# ============================================================

# Verificar se esta rodando em um sistema Debian/Ubuntu
check_distro() {
    log_step "Verificando sistema operacional..."
    
    if [ ! -f /etc/os-release ]; then
        log_error "Nao foi possivel detectar a distribuicao."
        exit 1
    fi
    
    source /etc/os-release
    
    case "$ID" in
        ubuntu|debian|linuxmint|pop|elementary|zorin)
            log_info "Distribuicao suportada detectada: $NAME"
            ;;
        *)
            log_warn "Distribuicao nao testada: $NAME"
            log_warn "Este instalador foi otimizado para Ubuntu/Debian."
            read -p "Deseja continuar mesmo assim? [S/n]: " resp
            resp=${resp:-S}
            if [[ ! "$resp" =~ ^[Ss]$ ]]; then
                exit 0
            fi
            ;;
    esac
    
    # Detectar versao Ubuntu
    UBUNTU_VERSION="${VERSION_ID:-unknown}"
    log_info "Versao: $UBUNTU_VERSION"
}

# Verificar se comando existe
command_exists() {
    command -v "$1" &> /dev/null
}

# Executar comando com sudo se necessario
run_sudo() {
    if [ "$EUID" -eq 0 ]; then
        "$@"
    else
        sudo "$@"
    fi
}

# Verificar se o usuario tem sudo
has_sudo() {
    if [ "$EUID" -eq 0 ]; then
        return 0
    fi
    sudo -n true 2>/dev/null
}

# ============================================================
# ETAPA 1: REMOVER VERSOES ANTIGAS
# ============================================================
remove_old_versions() {
    log_step "Verificando versoes anteriores..."
    
    local found_old=false
    
    # Verificar processo em execucao
    if pgrep -f "titan-launcher" &>/dev/null; then
        log_warn "Titan Launcher esta em execucao. Fechando..."
        pkill -f "titan-launcher" 2>/dev/null || true
        sleep 2
    fi
    
    # Remover diretorio antigo de instalacao
    if [ -d "$INSTALL_DIR" ]; then
        log_warn "Removendo instalacao anterior..."
        rm -rf "$INSTALL_DIR"
        found_old=true
    fi
    
    # Remover binarios antigos
    local old_bins=("titan-launcher" "titanlauncher" "TitanLauncher" "alchem-launcher" "alchem")
    for bin in "${old_bins[@]}"; do
        if [ -L "$BIN_DIR/$bin" ]; then
            rm -f "$BIN_DIR/$bin"
            found_old=true
        fi
        if [ -f "/usr/local/bin/$bin" ]; then
            run_sudo rm -f "/usr/local/bin/$bin" 2>/dev/null || true
            found_old=true
        fi
    done
    
    # Remover .desktop antigos
    local old_desktops=("titan-launcher.desktop" "titanlauncher.desktop" "alchem-launcher.desktop")
    for desktop in "${old_desktops[@]}"; do
        if [ -f "$DESKTOP_DIR/$desktop" ]; then
            rm -f "$DESKTOP_DIR/$desktop"
            found_old=true
        fi
    done
    
    # Atualizar database de aplicativos
    if command_exists update-desktop-database; then
        update-desktop-database "$DESKTOP_DIR" 2>/dev/null || true
    fi
    
    if [ "$found_old" = true ]; then
        log_info "Versao anterior removida com sucesso"
    else
        log_info "Nenhuma versao anterior encontrada"
    fi
}

# ============================================================
# ETAPA 2: VERIFICAR E INSTALAR DEPENDENCIAS DO SISTEMA
# ============================================================
install_system_deps() {
    log_step "Verificando dependencias do sistema..."
    
    # Verificar se temos sudo
    if ! has_sudo; then
        log_error "Permissao sudo necessaria para instalar dependencias."
        log_info "Execute: sudo apt update && sudo apt install -y python3 python3-pip python3-tk python3-venv openjdk-21-jre"
        exit 1
    fi
    
    # Atualizar repositorios
    log_info "Atualizando repositorios..."
    run_sudo apt-get update -qq | tee -a "$LOG_FILE"
    
    # Python 3
    if ! command_exists python3; then
        log_info "Instalando Python 3..."
        run_sudo apt-get install -y -qq python3 python3-venv | tee -a "$LOG_FILE"
    else
        local py_version
        py_version=$(python3 --version 2>&1 | awk '{print $2}')
        log_info "Python 3 encontrado: $py_version"
        
        # Verificar versao minima (3.8)
        local py_major py_minor
        py_major=$(echo "$py_version" | cut -d. -f1)
        py_minor=$(echo "$py_version" | cut -d. -f2)
        
        if [ "$py_major" -lt 3 ] || ([ "$py_major" -eq 3 ] && [ "$py_minor" -lt 8 ]); then
            log_error "Python 3.8+ e necessario! Versao atual: $py_version"
            exit 1
        fi
    fi
    
    # pip
    if ! command_exists pip3; then
        log_info "Instalando pip3..."
        run_sudo apt-get install -y -qq python3-pip | tee -a "$LOG_FILE"
    fi
    
    # tkinter
    if ! python3 -c "import tkinter" 2>/dev/null; then
        log_info "Instalando tkinter..."
        run_sudo apt-get install -y -qq python3-tk | tee -a "$LOG_FILE"
    else
        log_info "tkinter: OK"
    fi
    
    # venv (necessario para ambiente virtual)
    if ! python3 -m venv --help &>/dev/null; then
        log_info "Instalando python3-venv..."
        run_sudo apt-get install -y -qq python3-venv | tee -a "$LOG_FILE"
    fi
    
    # Java (OpenJDK)
    log_step "Verificando Java..."
    if command_exists java; then
        local java_version
        java_version=$(java -version 2>&1 | head -1 | sed 's/.*"\(.*\)".*/\1/')
        log_info "Java encontrado: $java_version"
    else
        log_warn "Java nao encontrado! Necessario para rodar Minecraft."
        read -p "Deseja instalar OpenJDK 21? [S/n]: " resp
        resp=${resp:-S}
        if [[ "$resp" =~ ^[Ss]$ ]]; then
            log_info "Instalando OpenJDK 21..."
            run_sudo apt-get install -y -qq openjdk-21-jre | tee -a "$LOG_FILE"
            log_info "Java instalado com sucesso!"
        else
            log_warn "Minecraft pode nao funcionar sem Java."
        fi
    fi
    
    # Git (para possiveis updates futuros)
    if ! command_exists git; then
        log_info "Instalando git..."
        run_sudo apt-get install -y -qq git | tee -a "$LOG_FILE"
    fi
}

# ============================================================
# ETAPA 3: CRIAR AMBIENTE VIRTUAL E INSTALAR DEPENDENCIAS PYTHON
# ============================================================
install_python_deps() {
    log_step "Configurando ambiente Python..."
    
    # Criar diretorios
    mkdir -p "$INSTALL_DIR"
    mkdir -p "$CONFIG_DIR"
    mkdir -p "$CONFIG_DIR/minecraft"
    mkdir -p "$CONFIG_DIR/backups"
    
    # Criar ambiente virtual
    log_info "Criando ambiente virtual..."
    python3 -m venv "$INSTALL_DIR/venv"
    
    # Ativar e instalar dependencias
    source "$INSTALL_DIR/venv/bin/activate"
    
    log_info "Atualizando pip..."
    pip install --upgrade pip wheel setuptools | tee -a "$LOG_FILE"
    
    # Instalar dependencias do requirements.txt ou padrao
    if [ -f "$SCRIPT_DIR/TitanLauncher/requirements.txt" ]; then
        log_info "Instalando dependencias do requirements.txt..."
        pip install -r "$SCRIPT_DIR/TitanLauncher/requirements.txt" | tee -a "$LOG_FILE"
    else
        log_info "Instalando dependencias padrao..."
        pip install minecraft-launcher-lib Pillow psutil | tee -a "$LOG_FILE"
    fi
    
    # Desativar venv
    deactivate
    
    log_info "Ambiente Python configurado!"
}

# ============================================================
# ETAPA 4: INSTALAR ARQUIVOS DO APLICATIVO
# ============================================================
install_app_files() {
    log_step "Instalando arquivos do aplicativo..."
    
    # Copiar codigo fonte
    if [ -d "$SCRIPT_DIR/TitanLauncher/src" ]; then
        mkdir -p "$INSTALL_DIR"
        cp -r "$SCRIPT_DIR/TitanLauncher/src" "$INSTALL_DIR/"
        log_info "Codigo fonte copiado"
    else
        log_error "Diretorio src nao encontrado!"
        exit 1
    fi
    
    # Copiar assets
    if [ -d "$SCRIPT_DIR/TitanLauncher/assets" ]; then
        mkdir -p "$INSTALL_DIR"
        cp -r "$SCRIPT_DIR/TitanLauncher/assets" "$INSTALL_DIR/"
        log_info "Assets copiados"
    fi
    
    # Copiar requirements.txt
    if [ -f "$SCRIPT_DIR/TitanLauncher/requirements.txt" ]; then
        cp "$SCRIPT_DIR/TitanLauncher/requirements.txt" "$INSTALL_DIR/"
    fi
}

# ============================================================
# ETAPA 5: CRIAR WRAPPER DE EXECUCAO
# ============================================================
create_launcher_wrapper() {
    log_step "Criando wrapper de execucao..."
    
    cat > "$INSTALL_DIR/titan-launcher" << EOF
#!/bin/bash
# Titan Launcher Wrapper
source "$INSTALL_DIR/venv/bin/activate"
python3 "$INSTALL_DIR/src/main.py" "\$@"
deactivate
EOF
    
    chmod +x "$INSTALL_DIR/titan-launcher"
    
    # Criar link simbólico em ~/.local/bin
    mkdir -p "$BIN_DIR"
    ln -sf "$INSTALL_DIR/titan-launcher" "$BIN_DIR/titan-launcher"
    
    log_info "Wrapper criado em $BIN_DIR/titan-launcher"
}

# ============================================================
# ETAPA 6: CRIAR ATALHO NO MENU (.desktop)
# ============================================================
create_desktop_entry() {
    log_step "Criando atalho no menu..."
    
    # Garantir diretorio de icones
    mkdir -p "$ICON_DIR"
    
    # Copiar icone
    if [ -f "$INSTALL_DIR/assets/icons/titan_icon.png" ]; then
        cp "$INSTALL_DIR/assets/icons/titan_icon.png" "$ICON_DIR/titan-launcher.png"
    fi
    
    # Criar arquivo .desktop
    mkdir -p "$DESKTOP_DIR"
    cat > "$DESKTOP_DIR/titan-launcher.desktop" << EOF
[Desktop Entry]
Name=Titan Launcher
Comment=Minecraft Launcher para Linux - Titan Edition
Exec=$BIN_DIR/titan-launcher
Icon=titan-launcher
Terminal=false
Type=Application
Categories=Game;
StartupWMClass=TitanLauncher
EOF
    
    chmod +x "$DESKTOP_DIR/titan-launcher.desktop"
    
    # Atualizar database
    if command_exists update-desktop-database; then
        update-desktop-database "$DESKTOP_DIR" 2>/dev/null || true
    fi
    
    log_info "Atalho criado com sucesso!"
}

# ============================================================
# ETAPA 7: VERIFICACAO FINAL
# ============================================================
verify_installation() {
    log_step "Verificando instalacao..."
    
    local errors=0
    
    [ ! -f "$INSTALL_DIR/titan-launcher" ] && { log_error "Wrapper nao encontrado"; ((errors++)); }
    [ ! -d "$INSTALL_DIR/venv" ] && { log_error "Venv nao encontrado"; ((errors++)); }
    [ ! -f "$DESKTOP_DIR/titan-launcher.desktop" ] && { log_error "Atalho .desktop nao encontrado"; ((errors++)); }
    
    if [ $errors -eq 0 ]; then
        return 0
    else
        return 1
    fi
}

setup_path() {
    log_step "Configurando PATH..."
    
    if [[ ":$PATH:" == *":$BIN_DIR:"* ]]; then
        log_info "~/.local/bin ja esta no PATH"
        return 0
    fi
    
    # Detectar shell
    local shell_rc="$HOME/.bashrc"
    if [ -n "${SHELL:-}" ]; then
        case "$SHELL" in
            */zsh) shell_rc="$HOME/.zshrc" ;;
            */fish) shell_rc="$HOME/.config/fish/config.fish" ;;
            */bash) shell_rc="$HOME/.bashrc" ;;
        esac
    fi
    
    # Adicionar ao PATH
    echo "" >> "$shell_rc"
    echo "# Titan Launcher PATH" >> "$shell_rc"
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$shell_rc"
    
    export PATH="$BIN_DIR:$PATH"
    
    log_info "~/.local/bin adicionado ao PATH ($shell_rc)"
    log_warn "Reinicie o terminal ou execute: source $shell_rc"
}

# ============================================================
# ETAPA 8: FUNCAO DE DESINSTALACAO
# ============================================================
uninstall() {
    log_step "Desinstalando Titan Launcher..."
    
    # Fechar se estiver rodando
    if pgrep -f "titan-launcher" &>/dev/null; then
        pkill -f "titan-launcher" 2>/dev/null || true
        sleep 1
    fi
    
    # Remover diretorio de instalacao
    if [ -d "$INSTALL_DIR" ]; then
        rm -rf "$INSTALL_DIR"
        log_info "Diretorio de instalacao removido"
    fi
    
    # Remover link
    if [ -L "$BIN_DIR/titan-launcher" ]; then
        rm -f "$BIN_DIR/titan-launcher"
        log_info "Link removido"
    fi
    
    # Remover .desktop
    if [ -f "$DESKTOP_DIR/titan-launcher.desktop" ]; then
        rm -f "$DESKTOP_DIR/titan-launcher.desktop"
        log_info "Menu de aplicativos removido"
    fi
    
    # Remover icone
    if [ -f "$ICON_DIR/titan-launcher.png" ]; then
        rm -f "$ICON_DIR/titan-launcher.png"
    fi
    
    # Atualizar database
    if command_exists update-desktop-database; then
        update-desktop-database "$DESKTOP_DIR" 2>/dev/null || true
    fi
    
    log_info "Desinstalacao concluida!"
}

# ============================================================
# ETAPA 9: FUNCAO DE ATUALIZACAO
# ============================================================
update() {
    log_step "Atualizando Titan Launcher..."
    
    # Salvar dados do usuario
    local temp_backup="/tmp/titan-backup-$(date +%s)"
    if [ -d "$CONFIG_DIR" ]; then
        cp -r "$CONFIG_DIR" "$temp_backup"
    fi
    
    # Reinstalar
    remove_old_versions
    install_app_files
    install_python_deps
    create_desktop_entry
    
    # Restaurar dados
    if [ -d "$temp_backup" ]; then
        rm -rf "$CONFIG_DIR"
        mv "$temp_backup" "$CONFIG_DIR"
    fi
    
    log_info "Atualizacao concluida!"
}

# ============================================================
# ETAPA 10: EXECUTAR APLICATIVO
# ============================================================
run_app() {
    log_step "Iniciando Titan Launcher..."
    
    if [ -f "$INSTALL_DIR/titan-launcher" ]; then
        "$INSTALL_DIR/titan-launcher" &
        local PID=$!
        sleep 2
        
        if kill -0 $PID 2>/dev/null; then
            log_info "Titan Launcher iniciado! (PID: $PID)"
        else
            log_error "Falha ao iniciar Titan Launcher"
        fi
    else
        log_error "Executavel nao encontrado!"
    fi
}

# ============================================================
# MENU PRINCIPAL
# ============================================================
show_help() {
    echo ""
    echo -e "${BOLD}Uso:${NC} ./install.sh [opcao]"
    echo ""
    echo -e "${BOLD}Opcoes:${NC}"
    echo "  (sem opcao)    Instalar Titan Launcher"
    echo "  --uninstall    Desinstalar Titan Launcher"
    echo "  --update       Atualizar Titan Launcher"
    echo "  --run          Instalar e executar"
    echo "  --help         Mostrar esta ajuda"
    echo ""
    echo -e "${BOLD}Exemplos:${NC}"
    echo "  ./install.sh                    # Instalacao padrao"
    echo "  ./install.sh --uninstall        # Remover completamente"
    echo "  ./install.sh --run              # Instalar e abrir"
    echo ""
}

main() {
    case "${1:-}" in
        --help|-h)
            show_help
            exit 0
            ;;
        --uninstall|-u)
            uninstall
            exit 0
            ;;
        --update)
            update
            exit 0
            ;;
        --run)
            ;;
        "")
            ;;
        *)
            log_error "Opcao desconhecida: $1"
            show_help
            exit 1
            ;;
    esac
    
    echo ""
    log_info "Iniciando instalacao do Titan Launcher..."
    echo ""
    
    # Etapas de instalacao
    check_distro
    echo ""
    remove_old_versions
    echo ""
    install_system_deps
    echo ""
    install_app_files
    echo ""
    install_python_deps
    echo ""
    create_desktop_entry
    echo ""
    setup_path
    echo ""
    
    # Verificar
    if verify_installation; then
        echo ""
        echo -e "${GREEN}${BOLD}=============================================================${NC}"
        echo -e "${GREEN}${BOLD}  Titan Launcher instalado com sucesso!${NC}"
        echo -e "${GREEN}${BOLD}=============================================================${NC}"
        echo ""
        log_info "Comando: titan-launcher"
        log_info "Menu: Aplicativos > Jogos > Titan Launcher"
        log_info "Dados: ~/.config/titanlauncher/"
        log_info "Log: $LOG_FILE"
        echo ""
        
        if [ "${1:-}" = "--run" ]; then
            run_app
        else
            read -p "Deseja executar agora? [S/n]: " resp
            resp=${resp:-S}
            if [[ "$resp" =~ ^[Ss]$ ]]; then
                run_app
            fi
        fi
    else
        echo ""
        log_error "Falha na verificacao da instalacao!"
        log_info "Verifique o log: $LOG_FILE"
        exit 1
    fi
}

# Executar
main "$@"
