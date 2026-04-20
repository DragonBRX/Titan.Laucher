# Titan Launcher - Ubuntu/Debian Edition v3.0

Minecraft Launcher otimizado para sistemas baseados em Debian e Ubuntu.

## 🚀 Instalação Rápida (Para Novos Usuários)

Se esta é sua primeira vez instalando, execute o comando abaixo:

```bash
git clone https://github.com/DragonBRX/Titan.Laucher.git ~/Titan.Laucher && cd ~/Titan.Laucher && chmod +x install.sh && ./install.sh
```

---

## 🛠️ Manual de Recuperação (Para Erros de "main.py")

Se você teve o erro `No such file or directory` para o `main.py`, siga estes 3 passos:

### Passo 1: Limpeza Total
Remova resíduos de instalações que falharam:
```bash
pkill -f "titan-launcher" 2>/dev/null || true
rm -rf ~/.local/share/TitanLauncher ~/.config/titanlauncher ~/.local/bin/titan-launcher
rm -f ~/.local/share/applications/titan-launcher.desktop
update-desktop-database ~/.local/share/applications || true
```

### Passo 2: Atualização do Código
Sincronize seu computador com as correções oficiais:
```bash
cd ~/Titan.Laucher && git fetch --all && git reset --hard origin/main && git pull origin main
```

### Passo 3: Reinstalação
Execute o instalador corrigido:
```bash
sudo apt update && sudo apt install -y python3 python3-pip python3-tk python3-venv openjdk-21-jre
cd ~/Titan.Laucher && chmod +x install.sh && ./install.sh
```

---

## ⚙️ Opções do Instalador

- `./install.sh` - Instalação padrão
- `./install.sh --run` - Instala e abre o launcher
- `./install.sh --uninstall` - Remove completamente do sistema
- `./install.sh --update` - Atualiza preservando seus dados
- `./install.sh --help` - Mostra todas as opções

## 📋 Requisitos
- **SO:** Ubuntu 22.04 / 24.04 ou derivados
- **Python:** 3.10+
- **Java:** OpenJDK 21 (Recomendado)

## 📄 Documentação
Para detalhes avançados, veja o [README_UBUNTU.md](README_UBUNTU.md).
