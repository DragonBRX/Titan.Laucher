# Titan Launcher v3.0 - Ubuntu/Debian Edition

## Instalacao Automatica (Recomendada)

### Primeira Instalacao

Para instalar o Titan Launcher pela primeira vez, copie e cole o comando abaixo no seu terminal. Ele irá clonar o repositório, instalar as dependências necessárias e configurar o launcher.

```bash
git clone https://github.com/DragonBRX/Titan.Laucher.git && cd Titan.Laucher && chmod +x install.sh && ./install.sh --run
```

### Atualizacao / Reinstalacao

Para atualizar ou reinstalar o Titan Launcher, use o script `reinstalar.sh`. Ele irá parar qualquer processo em execução, remover a instalação anterior, atualizar o repositório Git, reinstalar as dependências do sistema e executar o instalador principal de forma automática.

```bash
cd Titan.Laucher && chmod +x reinstalar.sh && ./reinstalar.sh
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
