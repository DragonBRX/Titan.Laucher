# Titan Launcher v3.0 - Ubuntu/Debian Edition

## Instalacao Automatica (Recomendada)

### Metodo 1: Um Comando

```bash
cd titan-ubuntu && chmod +x install.sh && ./install.sh
```

Pronto! O script faz TUDO automaticamente:
- Detecta sua distribuicao
- Instala dependencias do sistema (Python, tkinter, Java)
- Configura ambiente Python virtual
- Instala bibliotecas Python
- Cria atalho no menu de aplicativos

### Metodo 2: Instalar e Executar

```bash
cd titan-ubuntu && chmod +x install.sh && ./install.sh --run
```

---

## Opcoes do Instalador

```bash
./install.sh              # Instalacao padrao
./install.sh --run        # Instalar e executar
./install.sh --uninstall  # Remover completamente
./install.sh --update     # Atualizar versao
./install.sh --help       # Ajuda
```

---

## Requisitos

### Minimos
- Ubuntu 20.04+ / Debian 11+ / Linux Mint 20+
- 4GB RAM
- Python 3.8+

### Recomendados
- Ubuntu 22.04+ LTS
- 8GB+ RAM
- OpenJDK 21
- GPU com suporte a OpenGL 4.0+

---

## Dependencias Instaladas Automaticamente

O instalador instala automaticamente:
- python3
- python3-pip
- python3-tk
- python3-venv
- openjdk-21-jre (perguntado ao usuario)
- git

---

## Pos-Instalacao

### Executar
```bash
titan-launcher
```

Ou pelo menu: **Aplicativos > Jogos > Titan Launcher**

### Diretorios
- **Aplicativo**: `~/.local/share/TitanLauncher/`
- **Dados**: `~/.config/titanlauncher/`
- **Perfis**: `~/.config/titanlauncher/minecraft/`
- **Backups**: `~/.config/titanlauncher/backups/`

---

## Solucao de Problemas

### Java nao encontrado
```bash
sudo apt update
sudo apt install openjdk-21-jre
```

### tkinter nao encontrado
```bash
sudo apt install python3-tk
```

### Permissao negada no install.sh
```bash
chmod +x install.sh
```

### Reinstalar do zero
```bash
./install.sh --uninstall && ./install.sh
```

---

## Diferencas da Versao Ubuntu

- Instalador otimizado para apt (Ubuntu/Debian/Mint/Pop!_OS)
- Ambiente virtual Python isolado
- Java auto-detectado nos caminhos padrao do Ubuntu
- Tema Ubuntu com identificacao visual
- Suporte a X11 e Wayland
- Atalho integrado ao GNOME/KDE/XFCE

---

## Versao
**v3.0 Ubuntu Edition** - 2026
