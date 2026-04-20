#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TITAN LAUNCHER v3.0 - UBUNTU/DEBIAN EDITION
Interface Principal otimizada para Ubuntu
"""

import os
import sys
import json
import threading
import subprocess
import traceback
import uuid
from pathlib import Path
from typing import Optional, Dict, List
from datetime import datetime
from dataclasses import dataclass, asdict

# Configurar stdout/stderr para UTF-8
try:
    sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)
    sys.stderr = open(sys.stderr.fileno(), mode='w', encoding='utf-8', buffering=1)
except (OSError, AttributeError):
    pass

# Adicionar diretorio src ao path
sys.path.insert(0, str(Path(__file__).parent))

print("[TITAN] Iniciando Titan Launcher v3.0 Ubuntu Edition...")

# ============================================================
# IMPORTAR MODULOS AVANCADOS COM TRATAMENTO DE ERROS
# ============================================================

try:
    from themes import ThemeManager
    print("[TITAN] Sistema de temas carregado")
except ImportError as e:
    print(f"[TITAN] AVISO: modulo themes nao encontrado - {e}")
    ThemeManager = None

try:
    from notifications import NotificationManager
    print("[TITAN] Sistema de notificacoes carregado")
except ImportError as e:
    print(f"[TITAN] AVISO: modulo notifications nao encontrado - {e}")
    NotificationManager = None

try:
    from performance import PerformanceMonitor, PerformanceWidget
    print("[TITAN] Monitor de performance carregado")
except ImportError as e:
    print(f"[TITAN] AVISO: modulo performance nao encontrado - {e}")
    PerformanceMonitor = None
    PerformanceWidget = None

try:
    from shader_manager import ShaderManager
    print("[TITAN] Gerenciador de shaders carregado")
except ImportError as e:
    print(f"[TITAN] AVISO: modulo shader_manager nao encontrado - {e}")
    ShaderManager = None

try:
    from profile_manager import ProfileExporter, ProfileBackup
    print("[TITAN] Sistema de exportacao/backup carregado")
except ImportError as e:
    print(f"[TITAN] AVISO: modulo profile_manager nao encontrado - {e}")
    ProfileExporter = None
    ProfileBackup = None

try:
    from utils import SystemInfo, QuickActions, ConfigManager
    print("[TITAN] Utilitarios carregados")
except ImportError as e:
    print(f"[TITAN] AVISO: modulo utils nao encontrado - {e}")
    SystemInfo = None
    QuickActions = None
    ConfigManager = None

# Importar tkinter
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

print("[TITAN] tkinter carregado")

# Minecraft Launcher Lib
try:
    import minecraft_launcher_lib as mll
    print("[TITAN] minecraft_launcher_lib carregado")
except ImportError as e:
    print(f"[TITAN] ERRO CRITICO: minecraft_launcher_lib nao encontrado! - {e}")
    mll = None

# PIL
try:
    from PIL import Image, ImageTk
    print("[TITAN] PIL carregado")
except ImportError:
    Image = None
    ImageTk = None


# ============================================================
# DATA CLASS - PERFIL DE JOGO
# ============================================================

@dataclass
class GameProfile:
    """Perfil de jogo"""
    id: str
    name: str
    mc_version: str
    mod_loader: str
    loader_version: str
    java_path: str
    ram_gb: int
    username: str
    uuid: str
    game_directory: str
    created_at: str
    mods_directory: Optional[str] = None
    game_directory_custom: Optional[str] = None
    last_played: Optional[str] = None
    installed: bool = False


# ============================================================
# DIALOG DE PROGRESSO
# ============================================================

class ProgressDialog:
    """Janela de progresso para downloads"""
    
    def __init__(self, parent, title="Download em Progresso"):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("500x180")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.dialog.configure(bg='#2b2b2b')
        self.dialog.resizable(False, False)
        
        # Centralizar
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - 250
        y = (self.dialog.winfo_screenheight() // 2) - 90
        self.dialog.geometry(f"+{x}+{y}")
        
        # Label de status
        self.status_label = tk.Label(
            self.dialog,
            text="Preparando...",
            font=("Helvetica", 11, "bold"),
            bg='#2b2b2b',
            fg='white'
        )
        self.status_label.pack(pady=(20, 5))
        
        # Barra de progresso
        self.progress = ttk.Progressbar(
            self.dialog,
            mode='determinate',
            length=450
        )
        self.progress.pack(pady=10, padx=25)
        
        # Label de detalhes
        self.detail_label = tk.Label(
            self.dialog,
            text="",
            font=("Helvetica", 9),
            bg='#2b2b2b',
            fg='#aaaaaa'
        )
        self.detail_label.pack(pady=5)
        
        self.max_value = 100
        self.current_value = 0
        
    def set_status(self, text):
        self.status_label.config(text=text)
        self.dialog.update()
        
    def set_detail(self, text):
        self.detail_label.config(text=text)
        self.dialog.update()
        
    def set_max(self, value):
        self.max_value = value
        self.progress['maximum'] = value
        
    def set_progress(self, value):
        self.current_value = value
        self.progress['value'] = value
        self.dialog.update()
        
    def close(self):
        try:
            self.dialog.destroy()
        except tk.TclError:
            pass


# ============================================================
# GERENCIADOR DE JAVA
# ============================================================

class JavaManager:
    """Gerencia deteccao e instalacao de Java no Ubuntu"""
    
    JAVA_PATHS = [
        "/usr/lib/jvm/java-21-openjdk-amd64/bin/java",
        "/usr/lib/jvm/java-17-openjdk-amd64/bin/java",
        "/usr/lib/jvm/java-21-openjdk/bin/java",
        "/usr/lib/jvm/java-17-openjdk/bin/java",
        "/usr/lib/jvm/default-java/bin/java",
    ]
    
    @classmethod
    def find_java(cls):
        """Encontra instalacao de Java valida"""
        # Verificar no PATH primeiro
        try:
            result = subprocess.run(
                ["which", "java"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return "java"
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        # Verificar caminhos comuns
        for path in cls.JAVA_PATHS:
            if os.path.isfile(path) and os.access(path, os.X_OK):
                return path
        
        return None
    
    @classmethod
    def get_java_version(cls, java_path="java"):
        """Obtem versao do Java"""
        try:
            result = subprocess.run(
                [java_path, "-version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            # Java imprime versao no stderr
            for line in result.stderr.split('\n'):
                if 'version' in line.lower():
                    # Extrair numero da versao
                    if '"' in line:
                        return line.split('"')[1]
            return None
        except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
            return None
    
    @classmethod
    def check_and_notify(cls, parent=None):
        """Verifica Java e mostra notificacao se necessario"""
        java = cls.find_java()
        if java:
            version = cls.get_java_version(java)
            print(f"[TITAN] Java detectado: {version} em {java}")
            return True
        
        msg = """Java nao encontrado!

Para instalar no Ubuntu/Debian, execute no terminal:

sudo apt update
sudo apt install openjdk-21-jre

Ou use o instalador automatico do Titan Launcher."""
        
        if parent:
            messagebox.showwarning("Java Nao Encontrado", msg)
        else:
            print(f"[TITAN] {msg}")
        
        return False


# ============================================================
# TITAN LAUNCHER - CLASSE PRINCIPAL
# ============================================================

class TitanLauncher:
    """Launcher principal do Titan"""
    
    VERSION = "3.0"
    
    def __init__(self):
        print("[TITAN] Inicializando TitanLauncher...")
        
        # Diretorios
        self.config_dir = Path.home() / ".config" / "titanlauncher"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.minecraft_dir = self.config_dir / "minecraft"
        self.minecraft_dir.mkdir(exist_ok=True)
        
        # Configuracoes
        self.config = self.load_config()
        self.profiles: Dict[str, GameProfile] = {}
        self.load_profiles()
        
        # Versoes disponiveis
        self.available_versions = []
        self.versions_loading = False
        
        # Gerenciadores
        self.theme_manager = ThemeManager() if ThemeManager else None
        self.notification_manager = None
        self.performance_monitor = None
        self.backup_manager = None
        self.shader_manager = None
        
        if ConfigManager:
            self.config_manager = ConfigManager(self.config_dir / "advanced_config.json")
            if self.theme_manager:
                saved_theme = self.config_manager.get('theme', 'dark')
                self.theme_manager.set_theme(saved_theme)
        else:
            self.config_manager = None
        
        self.root = None
        self.status_label = None
        self.main_frame = None
        self.current_view = "home"
        
    def create_window(self):
        """Cria janela principal"""
        self.root = tk.Tk()
        self.root.title(f"Titan Launcher v{self.VERSION} - Ubuntu Edition")
        self.root.geometry("1100x700")
        self.root.minsize(900, 600)
        
        # Tentar usar tema escuro por padrao
        theme = self.theme_manager.get_theme() if self.theme_manager else {
            'bg_primary': '#1a1a1a',
            'bg_secondary': '#2b2b2b',
            'bg_tertiary': '#353535',
            'fg_primary': '#ffffff',
            'fg_secondary': '#aaaaaa',
            'accent': '#4a9eff',
            'success': '#4caf50',
            'warning': '#ff9800',
            'error': '#f44336',
            'border': '#454545',
        }
        
        self.root.configure(bg=theme.get('bg_primary', '#1a1a1a'))
        
        # Configurar icone
        self._set_window_icon()
        
        # Inicializar gerenciadores
        if NotificationManager:
            self.notification_manager = NotificationManager(self.root)
        
        if PerformanceMonitor:
            self.performance_monitor = PerformanceMonitor(self.root)
            self.performance_monitor.start_monitoring()
        
        if ProfileBackup:
            self.backup_manager = ProfileBackup(self.config_dir / "backups")
        
        if ShaderManager:
            self.shader_manager = ShaderManager(self.minecraft_dir)
        
        # Criar UI
        self.create_ui()
        
        # Notificacao de boas-vindas
        if self.notification_manager:
            self.notification_manager.show(
                "Bem-vindo!",
                f"Titan Launcher v{self.VERSION} Ubuntu Edition carregado!",
                "success"
            )
        
        # Verificar Java
        self.root.after(1000, lambda: JavaManager.check_and_notify(self.root))
        
        # Carregar versoes em background
        if mll:
            threading.Thread(target=self.load_versions, daemon=True).start()
        
    def _set_window_icon(self):
        """Define icone da janela"""
        icon_paths = [
            Path(__file__).parent.parent / "assets" / "icons" / "titan_icon.png",
            Path.home() / ".local" / "share" / "icons" / "hicolor" / "256x256" / "apps" / "titan-launcher.png",
        ]
        
        for icon_path in icon_paths:
            if icon_path.exists() and ImageTk:
                try:
                    img = Image.open(icon_path)
                    photo = ImageTk.PhotoImage(img)
                    self.root.iconphoto(True, photo)
                    self._icon_ref = photo  # Manter referencia
                    return
                except Exception:
                    pass
        
    def create_ui(self):
        """Cria interface do usuario"""
        theme = self.theme_manager.get_theme() if self.theme_manager else {
            'bg_primary': '#1a1a1a',
            'bg_secondary': '#2b2b2b',
            'bg_tertiary': '#353535',
            'fg_primary': '#ffffff',
            'fg_secondary': '#aaaaaa',
            'accent': '#4a9eff',
            'success': '#4caf50',
            'warning': '#ff9800',
            'error': '#f44336',
            'border': '#454545',
        }
        
        # Container principal
        main_container = tk.Frame(self.root, bg=theme.get('bg_primary', '#1a1a1a'))
        main_container.pack(fill='both', expand=True)
        
        # ===== HEADER =====
        header = tk.Frame(main_container, height=70, bg='#0d0d0d')
        header.pack(fill='x', padx=0, pady=0)
        header.pack_propagate(False)
        
        # Titulo
        title_label = tk.Label(
            header,
            text=f"TITAN LAUNCHER v{self.VERSION}",
            font=("Helvetica", 18, "bold"),
            bg='#0d0d0d',
            fg=theme.get('accent', '#4a9eff')
        )
        title_label.pack(side='left', padx=15, pady=10)
        
        # Subtitulo Ubuntu
        ubuntu_label = tk.Label(
            header,
            text="UBUNTU EDITION",
            font=("Helvetica", 8),
            bg='#0d0d0d',
            fg='#ff6b35'
        )
        ubuntu_label.pack(side='left', pady=10)
        
        # Botao de Configuracoes
        try:
            settings_btn = tk.Button(
                header,
                text="⚙",
                font=("Helvetica", 16),
                bg='#0d0d0d',
                fg='white',
                bd=0,
                cursor='hand2',
                command=self.show_settings,
                activebackground='#2b2b2b'
            )
            settings_btn.pack(side='right', padx=15)
        except Exception:
            pass
        
        # Botao Java
        try:
            java_btn = tk.Button(
                header,
                text="☕",
                font=("Helvetica", 16),
                bg='#0d0d0d',
                fg='#ff9800',
                bd=0,
                cursor='hand2',
                command=self.show_java_info,
                activebackground='#2b2b2b'
            )
            java_btn.pack(side='right', padx=5)
        except Exception:
            pass
        
        # ===== AREA DE CONTEUDO =====
        content_frame = tk.Frame(
            main_container,
            bg=theme.get('bg_primary', '#1a1a1a')
        )
        content_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # ===== SIDEBAR =====
        sidebar = tk.Frame(content_frame, width=200, bg=theme.get('bg_primary', '#1a1a1a'))
        sidebar.pack(side='left', fill='y', padx=(0, 10))
        sidebar.pack_propagate(False)
        
        # Logo area
        logo_frame = tk.Frame(sidebar, bg=theme.get('bg_primary', '#1a1a1a'), height=60)
        logo_frame.pack(fill='x', pady=(10, 5))
        logo_frame.pack_propagate(False)
        
        tk.Label(
            logo_frame,
            text="🎮",
            font=("Helvetica", 28),
            bg=theme.get('bg_primary', '#1a1a1a'),
            fg='white'
        ).pack()
        
        # Separador
        tk.Frame(sidebar, height=2, bg=theme.get('border', '#454545')).pack(fill='x', padx=10, pady=5)
        
        # Menu items
        menu_items = [
            ("🏠  Inicio", self.show_home),
            ("👤  Perfis", self.show_profiles),
            ("📦  Versoes", self.show_versions),
            ("🌈  Shaders", self.show_shaders),
            ("💾  Backups", self.show_backups),
        ]
        
        self.menu_buttons = []
        for text, command in menu_items:
            btn = tk.Button(
                sidebar,
                text=text,
                command=lambda c=command, t=text: self._menu_click(c, t),
                width=18,
                bg=theme.get('bg_tertiary', '#353535'),
                fg=theme.get('fg_primary', '#ffffff'),
                bd=0,
                padx=15,
                pady=10,
                anchor='w',
                font=("Helvetica", 10),
                cursor='hand2',
                activebackground=theme.get('accent', '#4a9eff'),
                activeforeground='white'
            )
            btn.pack(fill='x', pady=2, padx=5)
            self.menu_buttons.append(btn)
        
        # Separador antes do info
        tk.Frame(sidebar, height=2, bg=theme.get('border', '#454545')).pack(fill='x', padx=10, pady=5)
        
        # Info do sistema
        if SystemInfo:
            info_frame = tk.Frame(sidebar, bg=theme.get('bg_primary', '#1a1a1a'))
            info_frame.pack(fill='x', padx=10, pady=5, side='bottom')
            
            ram_text = "RAM: --"
            try:
                import psutil
                total_ram = psutil.virtual_memory().total / (1024**3)
                ram_text = f"RAM: {total_ram:.1f}GB"
            except:
                pass
            
            tk.Label(
                info_frame,
                text=ram_text,
                font=("Helvetica", 8),
                bg=theme.get('bg_primary', '#1a1a1a'),
                fg=theme.get('fg_secondary', '#aaaaaa')
            ).pack(anchor='w')
        
        # ===== MAIN FRAME =====
        self.main_frame = tk.Frame(
            content_frame,
            bg=theme.get('bg_secondary', '#2b2b2b')
        )
        self.main_frame.pack(side='left', fill='both', expand=True)
        
        # ===== FOOTER =====
        footer = tk.Frame(main_container, height=40, bg='#0d0d0d')
        footer.pack(fill='x', side='bottom', padx=0, pady=0)
        
        self.status_label = tk.Label(
            footer,
            text="Pronto - Ubuntu Edition",
            font=("Helvetica", 9),
            bg='#0d0d0d',
            fg='#aaaaaa'
        )
        self.status_label.pack(side='left', padx=10)
        
        # Widget de performance
        if PerformanceWidget and self.performance_monitor:
            try:
                perf_widget = PerformanceWidget(footer, self.performance_monitor)
                perf_widget.frame.config(bg='#0d0d0d')
                perf_widget.frame.pack(side='right', padx=10)
            except Exception as e:
                print(f"[TITAN] Erro ao criar widget de performance: {e}")
        
        # Mostrar tela inicial
        self.show_home()

    def _menu_click(self, command, name):
        """Handler de clique no menu"""
        try:
            # Resetar cores dos botoes
            theme = self.theme_manager.get_theme() if self.theme_manager else {
                'bg_tertiary': '#353535',
                'accent': '#4a9eff'
            }
            for btn in self.menu_buttons:
                btn.config(bg=theme.get('bg_tertiary', '#353535'))
            
            # Destacar botao ativo
            active_btn = None
            for btn in self.menu_buttons:
                if name in btn.cget('text'):
                    active_btn = btn
                    break
            if active_btn:
                active_btn.config(bg=theme.get('accent', '#4a9eff'))
            
            command()
        except Exception as e:
            print(f"[TITAN] Erro em {name}: {e}")
            traceback.print_exc()

    def set_status(self, text):
        """Atualiza texto da barra de status"""
        if self.status_label:
            self.status_label.config(text=text)
            self.root.update_idletasks()

    # ===== TELAS =====

    def clear_main_frame(self):
        """Limpa o frame principal"""
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def show_home(self):
        """Tela inicial"""
        self.clear_main_frame()
        self.current_view = "home"
        
        theme = self.theme_manager.get_theme() if self.theme_manager else {
            'bg_secondary': '#2b2b2b',
            'accent': '#4a9eff',
            'success': '#4caf50',
        }
        
        container = tk.Frame(self.main_frame, bg=theme.get('bg_secondary', '#2b2b2b'))
        container.pack(fill='both', expand=True, padx=30, pady=30)
        
        # Titulo
        tk.Label(
            container,
            text=f"Titan Launcher v{self.VERSION}",
            font=("Helvetica", 28, "bold"),
            bg=theme.get('bg_secondary', '#2b2b2b'),
            fg='white'
        ).pack(pady=(0, 5))
        
        tk.Label(
            container,
            text="Ubuntu Edition - Sua central de Minecraft no Linux",
            font=("Helvetica", 12),
            bg=theme.get('bg_secondary', '#2b2b2b'),
            fg=theme.get('accent', '#4a9eff')
        ).pack(pady=(0, 30))
        
        # Botao principal
        btn_frame = tk.Frame(container, bg=theme.get('bg_secondary', '#2b2b2b'))
        btn_frame.pack(pady=20)
        
        tk.Button(
            btn_frame,
            text="+ Criar Novo Perfil",
            command=self.create_new_profile,
            bg=theme.get('accent', '#4a9eff'),
            fg='white',
            font=("Helvetica", 12, "bold"),
            padx=25,
            pady=12,
            bd=0,
            cursor='hand2',
            activebackground='#357abd'
        ).pack(side='left', padx=5)
        
        if self.profiles:
            tk.Button(
                btn_frame,
                text="🎮 Jogar Ultimo Perfil",
                command=self.play_last_profile,
                bg=theme.get('success', '#4caf50'),
                fg='white',
                font=("Helvetica", 12, "bold"),
                padx=25,
                pady=12,
                bd=0,
                cursor='hand2',
                activebackground='#388e3c'
            ).pack(side='left', padx=5)
        
        # Cards de perfis
        if self.profiles:
            tk.Label(
                container,
                text="Perfis Recentes:",
                font=("Helvetica", 14, "bold"),
                bg=theme.get('bg_secondary', '#2b2b2b'),
                fg='white'
            ).pack(anchor='w', pady=(30, 15))
            
            # Mostrar ate 3 perfis
            sorted_profiles = sorted(
                self.profiles.values(),
                key=lambda p: p.last_played or '',
                reverse=True
            )
            
            for profile in list(sorted_profiles)[:3]:
                self._create_profile_card(container, profile)
        else:
            # Mensagem de boas-vindas para novos usuarios
            welcome_frame = tk.Frame(
                container,
                bg=theme.get('bg_secondary', '#2b2b2b'),
                padx=20,
                pady=20
            )
            welcome_frame.pack(fill='x', pady=30)
            
            tk.Label(
                welcome_frame,
                text="Bem-vindo ao Titan Launcher!",
                font=("Helvetica", 14, "bold"),
                bg=theme.get('bg_secondary', '#2b2b2b'),
                fg='white'
            ).pack(pady=10)
            
            tk.Label(
                welcome_frame,
                text=("Para comecar, clique em 'Criar Novo Perfil' acima.\n\n"
                      "Voce precisara de:\n"
                      "  - Java instalado (OpenJDK 17 ou 21)\n"
                      "  - Pelo menos 4GB de RAM livre"),
                font=("Helvetica", 10),
                bg=theme.get('bg_secondary', '#2b2b2b'),
                fg='#aaaaaa',
                justify='left'
            ).pack(pady=10)

    def _create_profile_card(self, parent, profile):
        """Cria card de perfil"""
        card = tk.Frame(parent, bg='#353535', padx=15, pady=12)
        card.pack(fill='x', pady=5)
        
        # Info do perfil
        info_frame = tk.Frame(card, bg='#353535')
        info_frame.pack(side='left', fill='y')
        
        tk.Label(
            info_frame,
            text=profile.name,
            font=("Helvetica", 12, "bold"),
            bg='#353535',
            fg='white'
        ).pack(anchor='w')
        
        status_text = f"{profile.mc_version} - {profile.mod_loader}"
        if profile.installed:
            status_text += " - Instalado"
        else:
            status_text += " - Nao instalado"
        
        tk.Label(
            info_frame,
            text=status_text,
            font=("Helvetica", 9),
            bg='#353535',
            fg='#aaaaaa'
        ).pack(anchor='w')
        
        # Botoes
        btn_text = "▶ Jogar" if profile.installed else "↓ Instalar"
        btn_bg = '#4caf50' if profile.installed else '#ff9800'
        
        tk.Button(
            card,
            text=btn_text,
            bg=btn_bg,
            fg='white',
            bd=0,
            padx=20,
            pady=5,
            font=("Helvetica", 10, "bold"),
            cursor='hand2',
            command=lambda p=profile: self.launch_profile(p)
        ).pack(side='right', padx=5)
        
        tk.Button(
            card,
            text="⚙",
            bg='#454545',
            fg='white',
            bd=0,
            padx=10,
            pady=5,
            font=("Helvetica", 10),
            cursor='hand2',
            command=lambda p=profile: self.edit_profile(p)
        ).pack(side='right', padx=5)

    def show_profiles(self):
        """Tela de gerenciamento de perfis"""
        self.clear_main_frame()
        self.current_view = "profiles"
        
        theme = self.theme_manager.get_theme() if self.theme_manager else {
            'bg_secondary': '#2b2b2b',
            'accent': '#4a9eff',
        }
        
        # Header
        header = tk.Frame(self.main_frame, bg=theme.get('bg_secondary', '#2b2b2b'))
        header.pack(fill='x', padx=20, pady=15)
        
        tk.Label(
            header,
            text="Gerenciar Perfis",
            font=("Helvetica", 20, "bold"),
            bg=theme.get('bg_secondary', '#2b2b2b'),
            fg='white'
        ).pack(side='left')
        
        tk.Button(
            header,
            text="+ Novo Perfil",
            command=self.create_new_profile,
            bg=theme.get('accent', '#4a9eff'),
            fg='white',
            bd=0,
            padx=15,
            pady=5,
            font=("Helvetica", 10, "bold"),
            cursor='hand2'
        ).pack(side='right')
        
        # Container
        container = tk.Frame(self.main_frame, bg=theme.get('bg_secondary', '#2b2b2b'))
        container.pack(fill='both', expand=True, padx=20, pady=10)
        
        if not self.profiles:
            tk.Label(
                container,
                text="Nenhum perfil criado ainda.",
                font=("Helvetica", 12),
                bg=theme.get('bg_secondary', '#2b2b2b'),
                fg='#aaaaaa'
            ).pack(pady=50)
            
            tk.Button(
                container,
                text="Criar Primeiro Perfil",
                command=self.create_new_profile,
                bg=theme.get('accent', '#4a9eff'),
                fg='white',
                font=("Helvetica", 12, "bold"),
                padx=20,
                pady=10,
                bd=0,
                cursor='hand2'
            ).pack(pady=20)
            return
        
        # Listar perfis
        for pid, profile in self.profiles.items():
            card = tk.Frame(container, bg='#353535', pady=10, padx=15)
            card.pack(fill='x', pady=5)
            
            # Info
            info = tk.Frame(card, bg='#353535')
            info.pack(side='left', fill='y')
            
            tk.Label(
                info,
                text=profile.name,
                font=("Helvetica", 12, "bold"),
                bg='#353535',
                fg='white'
            ).pack(anchor='w')
            
            tk.Label(
                info,
                text=f"[{profile.mc_version} - {profile.mod_loader} - {profile.ram_gb}GB RAM]",
                bg='#353535',
                fg='#aaaaaa',
                font=("Helvetica", 9)
            ).pack(anchor='w')
            
            # Botoes
            btn_frame = tk.Frame(card, bg='#353535')
            btn_frame.pack(side='right')
            
            btn_text = "▶ Jogar" if profile.installed else "↓ Instalar"
            btn_bg = '#4caf50' if profile.installed else '#ff9800'
            
            tk.Button(
                btn_frame,
                text=btn_text,
                bg=btn_bg,
                fg='white',
                bd=0,
                padx=12,
                pady=3,
                font=("Helvetica", 9, "bold"),
                cursor='hand2',
                command=lambda p=profile: self.launch_profile(p)
            ).pack(side='left', padx=2)
            
            tk.Button(
                btn_frame,
                text="🗑",
                bg='#f44336',
                fg='white',
                bd=0,
                padx=8,
                pady=3,
                font=("Helvetica", 9),
                cursor='hand2',
                command=lambda p=profile: self.delete_profile(p)
            ).pack(side='left', padx=2)

    def show_versions(self):
        """Tela de versoes disponiveis"""
        self.clear_main_frame()
        self.current_view = "versions"
        
        tk.Label(
            self.main_frame,
            text="Versoes Disponiveis",
            font=("Helvetica", 20, "bold"),
            bg='#2b2b2b',
            fg='white'
        ).pack(pady=20)
        
        if self.versions_loading:
            tk.Label(
                self.main_frame,
                text="Carregando versoes do Minecraft...",
                bg='#2b2b2b',
                fg='#aaaaaa',
                font=("Helvetica", 11)
            ).pack(pady=20)
        elif not self.available_versions:
            tk.Label(
                self.main_frame,
                text="Nenhuma versao carregada.",
                bg='#2b2b2b',
                fg='#aaaaaa'
            ).pack(pady=20)
            
            tk.Button(
                self.main_frame,
                text="Recarregar",
                command=lambda: threading.Thread(target=self.load_versions, daemon=True).start(),
                bg='#4a9eff',
                fg='white',
                bd=0,
                padx=15,
                pady=5,
                cursor='hand2'
            ).pack(pady=10)
        else:
            # Frame com scrollbar
            frame_container = tk.Frame(self.main_frame, bg='#2b2b2b')
            frame_container.pack(fill='both', expand=True, padx=20, pady=10)
            
            canvas = tk.Canvas(frame_container, bg='#2b2b2b', highlightthickness=0)
            scrollbar = ttk.Scrollbar(frame_container, orient="vertical", command=canvas.yview)
            scroll_frame = tk.Frame(canvas, bg='#2b2b2b')
            
            scroll_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )
            
            canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            
            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
            
            # Exibir versoes
            release_versions = [v for v in self.available_versions if v.get('type') == 'release']
            
            tk.Label(
                scroll_frame,
                text=f"Releases encontradas: {len(release_versions)}",
                bg='#2b2b2b',
                fg='#4a9eff',
                font=("Helvetica", 10, "bold")
            ).pack(anchor='w', pady=(0, 10))
            
            for v in release_versions[:50]:
                v_frame = tk.Frame(scroll_frame, bg='#353535', padx=10, pady=5)
                v_frame.pack(fill='x', pady=1)
                
                tk.Label(
                    v_frame,
                    text=v['id'],
                    bg='#353535',
                    fg='white',
                    font=("Helvetica", 10),
                    width=15,
                    anchor='w'
                ).pack(side='left')
                
                tk.Label(
                    v_frame,
                    text=v.get('type', 'unknown'),
                    bg='#353535',
                    fg='#4caf50',
                    font=("Helvetica", 9)
                ).pack(side='right')

    def show_shaders(self):
        """Tela de gerenciamento de shaders"""
        self.clear_main_frame()
        self.current_view = "shaders"
        
        tk.Label(
            self.main_frame,
            text="Gerenciador de Shaders",
            font=("Helvetica", 20, "bold"),
            bg='#2b2b2b',
            fg='white'
        ).pack(pady=20)
        
        if not self.profiles:
            tk.Label(
                self.main_frame,
                text="Crie um perfil primeiro para gerenciar shaders.",
                bg='#2b2b2b',
                fg='#aaaaaa',
                font=("Helvetica", 11)
            ).pack(pady=20)
            return
        
        # Info
        info_frame = tk.Frame(self.main_frame, bg='#2b2b2b')
        info_frame.pack(padx=20, pady=10, fill='x')
        
        tk.Label(
            info_frame,
            text="Shaders populares para Minecraft:",
            bg='#2b2b2b',
            fg='white',
            font=("Helvetica", 12, "bold")
        ).pack(anchor='w')
        
        shaders_info = [
            ("Leves (60+ FPS)", "BSL Shaders, MakeUp Ultra Fast, Vanilla Plus", "#4caf50"),
            ("Medios (30-60 FPS)", "Complementary, Sildur's Vibrant, ProjectLUMA", "#ff9800"),
            ("Pesados (GPU potente)", "SEUS PTGI, Continuum", "#f44336"),
        ]
        
        for title, shaders, color in shaders_info:
            frame = tk.Frame(info_frame, bg='#353535', padx=10, pady=8)
            frame.pack(fill='x', pady=5)
            
            tk.Label(
                frame,
                text=title,
                bg='#353535',
                fg=color,
                font=("Helvetica", 10, "bold")
            ).pack(anchor='w')
            
            tk.Label(
                frame,
                text=shaders,
                bg='#353535',
                fg='#aaaaaa',
                font=("Helvetica", 9)
            ).pack(anchor='w')
        
        # Instalacao manual
        tk.Label(
            info_frame,
            text="\nPara instalar shaders manualmente:",
            bg='#2b2b2b',
            fg='white',
            font=("Helvetica", 11, "bold")
        ).pack(anchor='w', pady=(20, 5))
        
        steps = [
            "1. Instale OptiFine ou Iris no seu perfil",
            "2. Baixe o shader pack (.zip) do site oficial",
            "3. Coloque na pasta 'shaderpacks' do perfil",
            "4. Selecione no menu de opcoes do Minecraft"
        ]
        
        for step in steps:
            tk.Label(
                info_frame,
                text=step,
                bg='#2b2b2b',
                fg='#aaaaaa',
                font=("Helvetica", 10)
            ).pack(anchor='w')

    def show_backups(self):
        """Tela de backups"""
        self.clear_main_frame()
        self.current_view = "backups"
        
        tk.Label(
            self.main_frame,
            text="Backups de Perfis",
            font=("Helvetica", 20, "bold"),
            bg='#2b2b2b',
            fg='white'
        ).pack(pady=20)
        
        if self.backup_manager:
            backups = self.backup_manager.list_backups()
            if not backups:
                tk.Label(
                    self.main_frame,
                    text="Nenhum backup encontrado.",
                    bg='#2b2b2b',
                    fg='#aaaaaa',
                    font=("Helvetica", 11)
                ).pack(pady=20)
                
                tk.Label(
                    self.main_frame,
                    text="Os backups sao criados automaticamente ao exportar perfis.",
                    bg='#2b2b2b',
                    fg='#888888',
                    font=("Helvetica", 9)
                ).pack()
            else:
                for b in backups:
                    b_frame = tk.Frame(self.main_frame, bg='#353535', padx=15, pady=10)
                    b_frame.pack(fill='x', padx=20, pady=5)
                    
                    tk.Label(
                        b_frame,
                        text=f"Backup: {b['name']}",
                        bg='#353535',
                        fg='white',
                        font=("Helvetica", 11, "bold")
                    ).pack(side='left')
                    
                    tk.Label(
                        b_frame,
                        text=f"{b.get('mc_version', '?')} - {b.get('backup_size', 0):.1f}MB",
                        bg='#353535',
                        fg='#aaaaaa',
                        font=("Helvetica", 9)
                    ).pack(side='right')
        else:
            tk.Label(
                self.main_frame,
                text="Sistema de backup nao disponivel.",
                bg='#2b2b2b',
                fg='#aaaaaa'
            ).pack(pady=20)

    # ===== DIALOGS =====

    def create_new_profile(self):
        """Dialog para criar novo perfil"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Novo Perfil - Titan Launcher")
        dialog.geometry("500x700")
        dialog.configure(bg='#2b2b2b')
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.resizable(False, False)
        
        # Centralizar
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - 250
        y = (dialog.winfo_screenheight() // 2) - 350
        dialog.geometry(f"+{x}+{y}")
        
        # Scrollable content
        canvas = tk.Canvas(dialog, bg='#2b2b2b', highlightthickness=0)
        scrollbar = ttk.Scrollbar(dialog, orient="vertical", command=canvas.yview)
        content = tk.Frame(canvas, bg='#2b2b2b')
        
        content.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=content, anchor="nw", width=480)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y")
        
        # Titulo
        tk.Label(
            content,
            text="Criar Novo Perfil",
            font=("Helvetica", 16, "bold"),
            bg='#2b2b2b',
            fg='#4a9eff'
        ).pack(pady=(10, 20))
        
        # Nome
        tk.Label(content, text="Nome do Perfil:", bg='#2b2b2b', fg='white', font=("Helvetica", 10)).pack(anchor='w', padx=20, pady=(10, 5))
        name_var = tk.StringVar(value="Meu Perfil")
        tk.Entry(content, textvariable=name_var, bg='#353535', fg='white', bd=0, font=("Helvetica", 11), insertbackground='white').pack(fill='x', padx=20, pady=5)
        
        # Versao
        tk.Label(content, text="Versao do Minecraft:", bg='#2b2b2b', fg='white', font=("Helvetica", 10)).pack(anchor='w', padx=20, pady=(15, 5))
        version_var = tk.StringVar(value="1.21.4")
        versions = ["1.21.4", "1.21.1", "1.20.6", "1.20.1", "1.19.4", "1.19.2", "1.18.2", "1.16.5", "1.12.2", "1.8.9"]
        v_menu = ttk.Combobox(content, textvariable=version_var, values=versions, state="readonly")
        v_menu.pack(fill='x', padx=20, pady=5)
        
        # Mod Loader
        tk.Label(content, text="Mod Loader:", bg='#2b2b2b', fg='white', font=("Helvetica", 10)).pack(anchor='w', padx=20, pady=(15, 5))
        loader_var = tk.StringVar(value="vanilla")
        l_menu = ttk.Combobox(content, textvariable=loader_var, values=["vanilla", "forge", "fabric"], state="readonly")
        l_menu.pack(fill='x', padx=20, pady=5)
        
        # RAM
        tk.Label(content, text="RAM (GB):", bg='#2b2b2b', fg='white', font=("Helvetica", 10)).pack(anchor='w', padx=20, pady=(15, 5))
        ram_var = tk.IntVar(value=4)
        ram_frame = tk.Frame(content, bg='#2b2b2b')
        ram_frame.pack(fill='x', padx=20, pady=5)
        tk.Spinbox(ram_frame, from_=2, to=32, textvariable=ram_var, bg='#353535', fg='white', font=("Helvetica", 11)).pack(side='left')
        tk.Label(ram_frame, text=" (Recomendado: 4-8GB)", bg='#2b2b2b', fg='#aaaaaa', font=("Helvetica", 9)).pack(side='left', padx=5)
        
        # Username
        tk.Label(content, text="Nome de Usuario:", bg='#2b2b2b', fg='white', font=("Helvetica", 10)).pack(anchor='w', padx=20, pady=(15, 5))
        username_var = tk.StringVar(value="Player")
        tk.Entry(content, textvariable=username_var, bg='#353535', fg='white', bd=0, font=("Helvetica", 11), insertbackground='white').pack(fill='x', padx=20, pady=5)
        
        # Diretorio customizado
        tk.Label(content, text="Diretorio do Jogo (opcional):", bg='#2b2b2b', fg='white', font=("Helvetica", 10, "bold")).pack(anchor='w', padx=20, pady=(20, 5))
        tk.Label(content, text="Deixe em branco para usar o padrao", bg='#2b2b2b', fg='#888888', font=("Helvetica", 9)).pack(anchor='w', padx=20)
        
        dir_var = tk.StringVar(value="")
        dir_frame = tk.Frame(content, bg='#2b2b2b')
        dir_frame.pack(fill='x', padx=20, pady=5)
        
        tk.Entry(dir_frame, textvariable=dir_var, bg='#353535', fg='white', bd=0, font=("Helvetica", 9), insertbackground='white').pack(side='left', fill='x', expand=True)
        
        def browse():
            path = filedialog.askdirectory()
            if path:
                dir_var.set(path)
        
        tk.Button(dir_frame, text="Procurar...", command=browse, bg='#454545', fg='white', bd=0, padx=10, cursor='hand2').pack(side='right', padx=(5, 0))
        
        # Java path
        java_path = JavaManager.find_java() or "java"
        tk.Label(content, text="Java:", bg='#2b2b2b', fg='white', font=("Helvetica", 10)).pack(anchor='w', padx=20, pady=(15, 5))
        java_var = tk.StringVar(value=java_path)
        tk.Entry(content, textvariable=java_var, bg='#353535', fg='white', bd=0, font=("Helvetica", 9), insertbackground='white', state='readonly').pack(fill='x', padx=20, pady=5)
        
        # Botao salvar
        def save():
            # Validacoes
            name = name_var.get().strip()
            if not name:
                messagebox.showerror("Erro", "Nome do perfil e obrigatorio!")
                return
            
            if name in [p.name for p in self.profiles.values()]:
                messagebox.showerror("Erro", f"Ja existe um perfil chamado '{name}'!")
                return
            
            custom_path = dir_var.get().strip()
            final_dir = custom_path if custom_path else str(self.minecraft_dir / name)
            
            profile = GameProfile(
                id=str(uuid.uuid4())[:8],
                name=name,
                mc_version=version_var.get(),
                mod_loader=loader_var.get(),
                loader_version="latest",
                java_path=java_var.get(),
                ram_gb=ram_var.get(),
                username=username_var.get().strip() or "Player",
                uuid=str(uuid.uuid4()),
                game_directory=final_dir,
                game_directory_custom=custom_path if custom_path else None,
                created_at=datetime.now().isoformat(),
                installed=False
            )
            
            self.profiles[profile.id] = profile
            self.save_profiles()
            dialog.destroy()
            
            if self.notification_manager:
                self.notification_manager.show("Sucesso", f"Perfil '{profile.name}' criado!", "success")
            
            self.show_profiles()
        
        tk.Button(
            content,
            text="SALVAR PERFIL",
            command=save,
            bg='#4a9eff',
            fg='white',
            font=("Helvetica", 12, "bold"),
            pady=12,
            bd=0,
            cursor='hand2',
            activebackground='#357abd'
        ).pack(fill='x', padx=20, pady=30)
        
        # Espaco extra para scroll
        tk.Frame(content, bg='#2b2b2b', height=20).pack()

    def edit_profile(self, profile):
        """Editar perfil existente"""
        # TODO: Implementar edicao completa
        messagebox.showinfo(
            "Editar Perfil",
            f"Perfil: {profile.name}\nVersao: {profile.mc_version}\nRAM: {profile.ram_gb}GB\nDiretorio: {profile.game_directory}\n\nUse 'Excluir' e recrie para alterar configuracoes."
        )

    def delete_profile(self, profile):
        """Excluir perfil"""
        if messagebox.askyesno("Confirmar", f"Excluir perfil '{profile.name}'?\n\nOs arquivos do Minecraft NAO serao excluidos."):
            del self.profiles[profile.id]
            self.save_profiles()
            
            if self.notification_manager:
                self.notification_manager.show("Excluido", f"Perfil '{profile.name}' removido", "info")
            
            self.show_profiles()

    def show_settings(self):
        """Configuracoes globais"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Configuracoes Globais")
        dialog.geometry("400x550")
        dialog.configure(bg='#2b2b2b')
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.resizable(False, False)
        
        # Centralizar
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - 200
        y = (dialog.winfo_screenheight() // 2) - 275
        dialog.geometry(f"+{x}+{y}")
        
        tk.Label(
            dialog,
            text="Configuracoes do Launcher",
            font=("Helvetica", 16, "bold"),
            bg='#2b2b2b',
            fg='white'
        ).pack(pady=20)
        
        # Tema
        tk.Label(dialog, text="Tema Visual:", bg='#2b2b2b', fg='white', font=("Helvetica", 11)).pack(pady=5)
        
        if self.theme_manager:
            themes = self.theme_manager.get_all_themes()
            theme_var = tk.StringVar(value=self.theme_manager.current_theme)
            cb = ttk.Combobox(dialog, textvariable=theme_var, values=[t[0] for t in themes], state="readonly")
            cb.pack(pady=5, fill='x', padx=30)
            
            def apply_theme():
                self.theme_manager.set_theme(theme_var.get())
                messagebox.showinfo("Tema", "Tema aplicado! Reinicie para efeito completo.")
                if self.config_manager:
                    self.config_manager.set('theme', theme_var.get())
            
            tk.Button(dialog, text="Aplicar Tema", command=apply_theme, bg='#4a9eff', fg='white', bd=0, padx=15, pady=5, cursor='hand2').pack(pady=10)
        
        # Separador
        tk.Frame(dialog, height=2, bg='#454545').pack(fill='x', padx=30, pady=15)
        
        # Diretorio de dados
        tk.Label(dialog, text="Diretorio de Dados:", bg='#2b2b2b', fg='white', font=("Helvetica", 11)).pack(pady=5)
        tk.Label(dialog, text=str(self.config_dir), bg='#2b2b2b', fg='#aaaaaa', font=("Helvetica", 9)).pack()
        
        tk.Button(
            dialog,
            text="Abrir Pasta",
            command=lambda: self._open_folder(self.config_dir),
            bg='#454545',
            fg='white',
            bd=0,
            padx=15,
            pady=5,
            cursor='hand2'
        ).pack(pady=5)
        
        # Separador
        tk.Frame(dialog, height=2, bg='#454545').pack(fill='x', padx=30, pady=15)
        
        # Java
        tk.Label(dialog, text="Java:", bg='#2b2b2b', fg='white', font=("Helvetica", 11)).pack(pady=5)
        
        java = JavaManager.find_java()
        java_version = JavaManager.get_java_version(java) if java else "Nao encontrado"
        
        tk.Label(dialog, text=f"Caminho: {java or 'N/A'}", bg='#2b2b2b', fg='#aaaaaa', font=("Helvetica", 9)).pack()
        tk.Label(dialog, text=f"Versao: {java_version or 'N/A'}", bg='#2b2b2b', fg='#aaaaaa', font=("Helvetica", 9)).pack()
        
        # Separador
        tk.Frame(dialog, height=2, bg='#454545').pack(fill='x', padx=30, pady=15)
        
        # Versao
        tk.Label(dialog, text=f"Titan Launcher v{self.VERSION}", bg='#2b2b2b', fg='#666666', font=("Helvetica", 9)).pack(pady=(20, 5))
        tk.Label(dialog, text="Ubuntu Edition", bg='#2b2b2b', fg='#ff6b35', font=("Helvetica", 8)).pack()

    def show_java_info(self):
        """Mostra informacoes sobre Java"""
        java = JavaManager.find_java()
        
        if java:
            version = JavaManager.get_java_version(java)
            messagebox.showinfo(
                "Java Instalado",
                f"Java encontrado!\n\nCaminho: {java}\nVersao: {version}\n\nStatus: OK para rodar Minecraft"
            )
        else:
            result = messagebox.askyesno(
                "Java Nao Encontrado",
                "Java nao esta instalado ou nao foi encontrado.\n\n"
                "Para instalar no Ubuntu, execute no terminal:\n\n"
                "sudo apt update && sudo apt install openjdk-21-jre\n\n"
                "Deseja copiar o comando para a area de transferencia?"
            )
            if result:
                self.root.clipboard_clear()
                self.root.clipboard_append("sudo apt update && sudo apt install -y openjdk-21-jre")
                messagebox.showinfo("Copiado", "Comando copiado! Cole no terminal com Ctrl+Shift+V")

    def _open_folder(self, path):
        """Abre pasta no gerenciador de arquivos"""
        try:
            subprocess.Popen(["xdg-open", str(path)])
        except Exception as e:
            messagebox.showerror("Erro", f"Nao foi possivel abrir a pasta: {e}")

    # ===== ACAO PRINCIPAL =====

    def play_last_profile(self):
        """Joga o ultimo perfil usado"""
        if not self.profiles:
            messagebox.showinfo("Perfis", "Nenhum perfil criado ainda.")
            return
        
        sorted_profiles = sorted(
            self.profiles.values(),
            key=lambda p: p.last_played or p.created_at,
            reverse=True
        )
        
        if sorted_profiles:
            self.launch_profile(sorted_profiles[0])

    def launch_profile(self, profile):
        """Inicia perfil (instala se necessario)"""
        if not profile.installed:
            self.install_minecraft(profile)
        else:
            self.run_minecraft(profile)

    def install_minecraft(self, profile):
        """Instala Minecraft para o perfil"""
        if not mll:
            messagebox.showerror("Erro", "minecraft_launcher_lib nao disponivel!")
            return
        
        # Verificar Java
        if not JavaManager.find_java():
            messagebox.showerror(
                "Java Necessario",
                "Java nao encontrado! Instale com:\n\nsudo apt install openjdk-21-jre"
            )
            return
        
        progress = ProgressDialog(self.root, f"Instalando {profile.name}")
        
        def do_install():
            try:
                path = Path(profile.game_directory)
                path.mkdir(parents=True, exist_ok=True)
                
                self.set_status(f"Instalando {profile.mc_version}...")
                
                mll.install.install_minecraft_version(
                    profile.mc_version,
                    str(path),
                    callback={
                        'setMax': progress.set_max,
                        'setProgress': progress.set_progress
                    }
                )
                
                profile.installed = True
                self.save_profiles()
                
                progress.close()
                self.root.after(0, lambda: messagebox.showinfo("Sucesso", f"Minecraft {profile.mc_version} instalado com sucesso!"))
                self.root.after(0, self.show_profiles)
                self.set_status("Instalacao concluida")
                
                if self.notification_manager:
                    self.notification_manager.show("Sucesso", f"{profile.name} instalado!", "success")
                
            except Exception as e:
                progress.close()
                self.root.after(0, lambda err=str(e): messagebox.showerror("Erro na Instalacao", err))
                self.set_status("Erro na instalacao")
        
        threading.Thread(target=do_install, daemon=True).start()

    def run_minecraft(self, profile):
        """Executa Minecraft"""
        if not mll:
            messagebox.showerror("Erro", "minecraft_launcher_lib nao disponivel!")
            return
        
        try:
            # Verificar Java
            java_path = JavaManager.find_java()
            if not java_path:
                messagebox.showerror("Erro", "Java nao encontrado!")
                return
            
            # Atualizar ultimo acesso
            profile.last_played = datetime.now().isoformat()
            self.save_profiles()
            
            self.set_status(f"Iniciando {profile.name}...")
            
            # Usar Java detectado
            java_bin = profile.java_path if profile.java_path != "java" else java_path
            
            options = {
                'username': profile.username,
                'uuid': profile.uuid,
                'token': '',
                'jvmArguments': [
                    f"-Xmx{profile.ram_gb}G",
                    f"-Xms{max(1, profile.ram_gb // 2)}G"
                ],
                'gameDirectory': profile.game_directory,
                'executablePath': java_bin
            }
            
            command = mll.command.get_minecraft_command(
                profile.mc_version,
                profile.game_directory,
                options
            )
            
            subprocess.Popen(command, cwd=profile.game_directory)
            
            if self.notification_manager:
                self.notification_manager.show("Iniciando", f"Abrindo {profile.name}...", "info")
            
            self.set_status(f"{profile.name} executando")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao iniciar Minecraft:\n{str(e)}")
            self.set_status("Erro ao iniciar")
            traceback.print_exc()

    # ===== CARREGAMENTO =====

    def load_versions(self):
        """Carrega versoes disponiveis em background"""
        self.versions_loading = True
        self.set_status("Carregando versoes...")
        
        try:
            if mll:
                self.available_versions = mll.utils.get_version_list()
                releases = [v for v in self.available_versions if v.get('type') == 'release']
                self.set_status(f"{len(releases)} versoes carregadas")
        except Exception as e:
            print(f"[TITAN] Erro ao carregar versoes: {e}")
            self.set_status("Erro ao carregar versoes")
        finally:
            self.versions_loading = False

    # ===== PERSISTENCIA =====

    def load_config(self):
        """Carrega configuracoes"""
        path = self.config_dir / "launcher_config.json"
        if path.exists():
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        return {
            'theme': 'dark',
            'java_auto_detect': True,
            'show_notifications': True,
        }

    def load_profiles(self):
        """Carrega perfis salvos"""
        path = self.config_dir / "profiles.json"
        if path.exists():
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for pid, pdata in data.items():
                        # Filtrar apenas campos validos
                        valid_fields = {f.name for f in GameProfile.__dataclass_fields__.values()}
                        filtered = {k: v for k, v in pdata.items() if k in valid_fields}
                        self.profiles[pid] = GameProfile(**filtered)
            except (json.JSONDecodeError, IOError, TypeError) as e:
                print(f"[TITAN] Erro ao carregar perfis: {e}")

    def save_profiles(self):
        """Salva perfis"""
        path = self.config_dir / "profiles.json"
        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(
                    {pid: asdict(p) for pid, p in self.profiles.items()},
                    f,
                    indent=2,
                    ensure_ascii=False
                )
        except IOError as e:
            print(f"[TITAN] Erro ao salvar perfis: {e}")

    # ===== EXECUCAO =====

    def run(self):
        """Inicia o launcher"""
        self.create_window()
        self.root.mainloop()


# ============================================================
# PONTO DE ENTRADA
# ============================================================

if __name__ == "__main__":
    try:
        launcher = TitanLauncher()
        launcher.run()
    except Exception as e:
        print(f"[TITAN] ERRO FATAL: {e}")
        traceback.print_exc()
        
        # Tentar mostrar erro em GUI
        try:
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror(
                "Erro Critico",
                f"Ocorreu um erro fatal:\n\n{str(e)}\n\n"
                f"Verifique se todas as dependencias estao instaladas:\n"
                f"  sudo apt install python3-tk\n"
                f"  pip3 install minecraft-launcher-lib Pillow psutil"
            )
        except Exception:
            pass
        
        sys.exit(1)
