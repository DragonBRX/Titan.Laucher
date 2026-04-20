#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TITAN LAUNCHER
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

print("[TITAN] Iniciando Titan Launcher Ubuntu Edition...")

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
        
        # Inicializar componentes em background
        threading.Thread(target=self._init_background_components, daemon=True).start()

    def _init_background_components(self):
        """Inicializa componentes pesados em background"""
        # Notificacoes
        if NotificationManager:
            self.notification_manager = NotificationManager()
        
        # Performance
        if PerformanceMonitor:
            self.performance_monitor = PerformanceMonitor()
            self.performance_monitor.start()
        
        # Backups
        if ProfileBackup:
            self.backup_manager = ProfileBackup(self.config_dir / "backups")
        
        # Shaders
        if ShaderManager:
            self.shader_manager = ShaderManager()
        
        # Carregar versoes do Minecraft
        self.load_versions()
        
        print("[TITAN] Componentes de background inicializados")

    def create_window(self):
        """Cria a janela principal"""
        self.root = tk.Tk()
        self.root.title("Titan Launcher - Ubuntu Edition")
        self.root.geometry("1100x700")
        self.root.minsize(900, 600)
        
        # Cores base (Dark Theme Ubuntu style)
        self.root.configure(bg='#1a1a1a')
        
        # Icone
        self._set_window_icon()
        
        # Estilo ttk
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TProgressbar", thickness=10, troughcolor='#2b2b2b', background='#4a9eff', bordercolor='#2b2b2b')
        style.configure("TCombobox", fieldbackground='#353535', background='#454545', foreground='white', bordercolor='#454545')
        
        # Layout principal
        self._build_layout()
        
        # Notificacao de inicializacao
        self.root.after(1000, lambda: print("[TITAN] Titan Launcher Ubuntu Edition carregado!"))
        
        # Verificar Java
        self.root.after(2000, lambda: JavaManager.check_and_notify(self.root))

    def _set_window_icon(self):
        """Define o icone da janela"""
        icon_paths = [
            os.path.expanduser("~/.local/share/TitanLauncher/assets/icons/titan_icon.png"),
            Path(__file__).parent.parent / "assets" / "icons" / "titan_icon.png",
            "/usr/share/icons/hicolor/256x256/apps/titan-launcher.png",
            "assets/icons/titan_icon.png"
        ]
        
        icon_loaded = False
        for path in icon_paths:
            if os.path.exists(path):
                try:
                    if Image and ImageTk:
                        img = Image.open(path)
                        photo = ImageTk.PhotoImage(img)
                        self.root.iconphoto(True, photo)
                        self.root._icon_photo = photo # Keep reference
                        icon_loaded = True
                        print(f"[TITAN] Icone carregado de: {path}")
                        break
                    else:
                        # Fallback tk.PhotoImage (suporta PNG no tk 8.6+)
                        photo = tk.PhotoImage(file=path)
                        self.root.iconphoto(True, photo)
                        self.root._icon_photo = photo
                        icon_loaded = True
                        print(f"[TITAN] Icone carregado (tk) de: {path}")
                        break
                except Exception as e:
                    print(f"[TITAN] Erro ao carregar icone {path}: {e}")
        
        if not icon_loaded:
            print("[TITAN] Aviso: Icone nao encontrado, usando padrao do sistema")

    def _build_layout(self):
        """Constroi a interface principal"""
        theme = self.theme_manager.get_theme() if self.theme_manager else {
            'bg_primary': '#1a1a1a',
            'bg_secondary': '#2b2b2b',
            'bg_tertiary': '#353535',
            'accent': '#4a9eff',
            'fg_primary': '#ffffff',
            'fg_secondary': '#aaaaaa',
            'border': '#454545'
        }
        
        # Container principal
        main_container = tk.Frame(self.root, bg=theme.get('bg_primary', '#1a1a1a'))
        main_container.pack(fill='both', expand=True)
        
        # Top bar (opcional, estilo Ubuntu)
        # top_bar = tk.Frame(main_container, height=30, bg='#000000')
        # top_bar.pack(fill='x', side='top')
        
        # Content Area (Sidebar + Main)
        content_frame = tk.Frame(main_container, bg=theme.get('bg_primary', '#1a1a1a'))
        content_frame.pack(fill='both', expand=True)
        
        # ===== SIDEBAR =====
        sidebar = tk.Frame(
            content_frame,
            width=220,
            bg=theme.get('bg_primary', '#1a1a1a'),
            padx=0,
            pady=0
        )
        sidebar.pack(side='left', fill='y')
        sidebar.pack_propagate(False)
        
        # Logo area
        logo_frame = tk.Frame(sidebar, bg=theme.get('bg_primary', '#1a1a1a'), height=60)
        logo_frame.pack(fill='x', pady=(10, 5))
        logo_frame.pack_propagate(False)
        
        tk.Label(
            logo_frame,
            text="TL",
            font=("Helvetica", 24, "bold"),
            bg=theme.get('bg_primary', '#1a1a1a'),
            fg='white'
        ).pack()
        
        # Separador
        tk.Frame(sidebar, height=2, bg=theme.get('border', '#454545')).pack(fill='x', padx=10, pady=5)
        
        # Menu items
        menu_items = [
            ("Inicio", self.show_home),
            ("Perfis", self.show_profiles),
            ("Versoes", self.show_versions),
            ("Shaders", self.show_shaders),
            ("Backups", self.show_backups),
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
            text="Titan Launcher",
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
                text="Jogar Ultimo Perfil",
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
        btn_text = "Jogar" if profile.installed else "Instalar"
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
            command=lambda p=profile: self.play_profile(p) if p.installed else self.install_minecraft(p)
        ).pack(side='right', padx=5)
        
        tk.Button(
            card,
            text="Editar",
            bg='#454545',
            fg='white',
            bd=0,
            padx=10,
            pady=5,
            font=("Helvetica", 9),
            cursor='hand2',
            command=lambda p=profile: self.edit_profile(p)
        ).pack(side='right', padx=5)

    def show_profiles(self):
        """Tela de lista de perfis"""
        self.clear_main_frame()
        self.current_view = "profiles"
        
        header = tk.Frame(self.main_frame, bg='#2b2b2b', padx=30, pady=20)
        header.pack(fill='x')
        
        tk.Label(
            header,
            text="Meus Perfis",
            font=("Helvetica", 20, "bold"),
            bg='#2b2b2b',
            fg='white'
        ).pack(side='left')
        
        tk.Button(
            header,
            text="+ Novo Perfil",
            command=self.create_new_profile,
            bg='#4a9eff',
            fg='white',
            font=("Helvetica", 10, "bold"),
            padx=15,
            pady=8,
            bd=0,
            cursor='hand2'
        ).pack(side='right')
        
        # Scrollable list
        canvas = tk.Canvas(self.main_frame, bg='#2b2b2b', highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.main_frame, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg='#2b2b2b')
        
        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw", width=800)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True, padx=30)
        scrollbar.pack(side="right", fill="y")
        
        if not self.profiles:
            tk.Label(
                scroll_frame,
                text="Nenhum perfil criado ainda.",
                bg='#2b2b2b',
                fg='#aaaaaa',
                font=("Helvetica", 12)
            ).pack(pady=50)
            return
            
        for profile in self.profiles.values():
            p_frame = tk.Frame(scroll_frame, bg='#353535', padx=20, pady=15)
            p_frame.pack(fill='x', pady=5)
            
            # Avatar (simulado)
            avatar_frame = tk.Frame(p_frame, width=48, height=48, bg='#454545')
            avatar_frame.pack(side='left', padx=(0, 15))
            avatar_frame.pack_propagate(False)
            
            # Tentar carregar avatar do steve
            steve_path = Path(__file__).parent.parent / "assets" / "avatars" / "steve.png"
            if steve_path.exists() and Image and ImageTk:
                try:
                    img = Image.open(steve_path).resize((48, 48), Image.NEAREST)
                    photo = ImageTk.PhotoImage(img)
                    lbl = tk.Label(avatar_frame, image=photo, bg='#454545')
                    lbl.image = photo
                    lbl.pack()
                except:
                    tk.Label(avatar_frame, text="MC", fg='white', bg='#454545').pack(expand=True)
            else:
                tk.Label(avatar_frame, text="MC", fg='white', bg='#454545').pack(expand=True)
            
            # Info
            info = tk.Frame(p_frame, bg='#353535')
            info.pack(side='left', fill='y')
            
            tk.Label(info, text=profile.name, font=("Helvetica", 12, "bold"), bg='#353535', fg='white').pack(anchor='w')
            tk.Label(info, text=f"Versao: {profile.mc_version} | Loader: {profile.mod_loader}", font=("Helvetica", 9), bg='#353535', fg='#aaaaaa').pack(anchor='w')
            
            # Actions
            actions = tk.Frame(p_frame, bg='#353535')
            actions.pack(side='right')
            
            btn_text = "Jogar" if profile.installed else "Instalar"
            btn_bg = '#4caf50' if profile.installed else '#ff9800'
            
            tk.Button(
                actions,
                text=btn_text,
                bg=btn_bg,
                fg='white',
                font=("Helvetica", 10, "bold"),
                padx=15,
                bd=0,
                cursor='hand2',
                command=lambda p=profile: self.play_profile(p) if p.installed else self.install_minecraft(p)
            ).pack(side='left', padx=5)
            
            tk.Button(
                actions,
                text="Config",
                bg='#454545',
                fg='white',
                font=("Helvetica", 9),
                padx=10,
                bd=0,
                cursor='hand2',
                command=lambda p=profile: self.edit_profile(p)
            ).pack(side='left', padx=5)
            
            tk.Button(
                actions,
                text="Excluir",
                bg='#f44336',
                fg='white',
                font=("Helvetica", 9),
                padx=10,
                bd=0,
                cursor='hand2',
                command=lambda p=profile: self.delete_profile(p)
            ).pack(side='left', padx=5)

    def show_versions(self):
        """Tela de versoes do Minecraft"""
        self.clear_main_frame()
        self.current_view = "versions"
        
        tk.Label(
            self.main_frame,
            text="Versoes do Minecraft",
            font=("Helvetica", 20, "bold"),
            bg='#2b2b2b',
            fg='white'
        ).pack(pady=20)
        
        if self.versions_loading:
            tk.Label(self.main_frame, text="Carregando lista de versoes...", bg='#2b2b2b', fg='#aaaaaa').pack(pady=20)
            return
            
        if not self.available_versions:
            tk.Label(self.main_frame, text="Nao foi possivel carregar as versoes.", bg='#2b2b2b', fg='#f44336').pack(pady=20)
            tk.Button(self.main_frame, text="Tentar Novamente", command=self.load_versions).pack()
            return
            
        # Listar algumas versoes
        canvas = tk.Canvas(self.main_frame, bg='#2b2b2b', highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.main_frame, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg='#2b2b2b')
        
        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw", width=800)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True, padx=30)
        scrollbar.pack(side="right", fill="y")
        
        release_versions = [v for v in self.available_versions if v.get('type') == 'release']
        
        if release_versions:
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
        
        def save():
            name = name_var.get().strip()
            if not name:
                messagebox.showerror("Erro", "Nome do perfil obrigatorio!")
                return
            
            pid = str(uuid.uuid4())[:8]
            mc_ver = version_var.get()
            loader = loader_var.get()
            
            # Definir diretorio
            custom_dir = dir_var.get().strip()
            if custom_dir:
                game_dir = custom_dir
            else:
                game_dir = str(self.minecraft_dir / pid)
            
            profile = GameProfile(
                id=pid,
                name=name,
                mc_version=mc_ver,
                mod_loader=loader,
                loader_version="latest",
                java_path="java",
                ram_gb=ram_var.get(),
                username=username_var.get().strip() or "Player",
                uuid=str(uuid.uuid4()),
                game_directory=game_dir,
                game_directory_custom=custom_dir if custom_dir else None,
                created_at=datetime.now().isoformat(),
                installed=False
            )
            
            self.profiles[pid] = profile
            self.save_profiles()
            dialog.destroy()
            
            if self.notification_manager:
                self.notification_manager.show("Sucesso", f"Perfil '{name}' criado!", "success")
            
            self.show_profiles()
            
        tk.Button(
            content,
            text="CRIAR PERFIL",
            command=save,
            bg='#4a9eff',
            fg='white',
            font=("Helvetica", 12, "bold"),
            pady=12,
            bd=0,
            cursor='hand2',
            activebackground='#357abd'
        ).pack(fill='x', padx=20, pady=30)

    # ===== ACOES DE PERFIL =====

    def play_last_profile(self):
        """Joga o ultimo perfil acessado"""
        if not self.profiles:
            return
            
        sorted_profiles = sorted(
            self.profiles.values(),
            key=lambda p: p.last_played or '',
            reverse=True
        )
        
        profile = sorted_profiles[0]
        self.play_profile(profile)

    def play_profile(self, profile):
        """Executa um perfil"""
        if not profile.installed:
            self.install_minecraft(profile)
            return
            
        self.run_minecraft(profile)

    def edit_profile(self, profile):
        """Editar perfil existente"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Editar Perfil")
        dialog.geometry("500x600")
        dialog.configure(bg='#2b2b2b')
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.resizable(False, False)
        
        # Centralizar
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - 250
        y = (dialog.winfo_screenheight() // 2) - 300
        dialog.geometry(f"+{x}+{y}")
        
        tk.Label(dialog, text="Editar Perfil", font=("Helvetica", 16, "bold"),
                 bg='#2b2b2b', fg='#4a9eff').pack(pady=(20, 15))
        
        # Nome
        tk.Label(dialog, text="Nome:", bg='#2b2b2b', fg='white', font=("Helvetica", 10)).pack(anchor='w', padx=20, pady=(10,5))
        name_var = tk.StringVar(value=profile.name)
        tk.Entry(dialog, textvariable=name_var, bg='#353535', fg='white', bd=0, font=("Helvetica", 11), insertbackground='white').pack(fill='x', padx=20, pady=5)
        
        # Versão
        tk.Label(dialog, text="Versao do Minecraft:", bg='#2b2b2b', fg='white', font=("Helvetica", 10)).pack(anchor='w', padx=20, pady=(10,5))
        version_var = tk.StringVar(value=profile.mc_version)
        versions = ["1.21.4", "1.21.1", "1.20.6", "1.20.1", "1.19.4", "1.19.2", "1.18.2", "1.16.5", "1.12.2", "1.8.9"]
        ttk.Combobox(dialog, textvariable=version_var, values=versions, state="readonly").pack(fill='x', padx=20, pady=5)
        
        # Mod Loader
        tk.Label(dialog, text="Mod Loader:", bg='#2b2b2b', fg='white', font=("Helvetica", 10)).pack(anchor='w', padx=20, pady=(10,5))
        loader_var = tk.StringVar(value=profile.mod_loader)
        ttk.Combobox(dialog, textvariable=loader_var, values=["vanilla", "forge", "fabric"], state="readonly").pack(fill='x', padx=20, pady=5)
        
        # RAM
        tk.Label(dialog, text="RAM (GB):", bg='#2b2b2b', fg='white', font=("Helvetica", 10)).pack(anchor='w', padx=20, pady=(10,5))
        ram_var = tk.IntVar(value=profile.ram_gb)
        tk.Spinbox(dialog, from_=2, to=32, textvariable=ram_var, bg='#353535', fg='white', font=("Helvetica", 11)).pack(fill='x', padx=20, pady=5)
        
        # Username
        tk.Label(dialog, text="Nome de Usuario:", bg='#2b2b2b', fg='white', font=("Helvetica", 10)).pack(anchor='w', padx=20, pady=(10,5))
        username_var = tk.StringVar(value=profile.username)
        tk.Entry(dialog, textvariable=username_var, bg='#353535', fg='white', bd=0, font=("Helvetica", 11), insertbackground='white').pack(fill='x', padx=20, pady=5)
        
        def save_changes():
            old_version = profile.mc_version
            old_loader = profile.mod_loader
            
            profile.name = name_var.get().strip() or profile.name
            profile.mc_version = version_var.get()
            profile.mod_loader = loader_var.get()
            profile.ram_gb = ram_var.get()
            profile.username = username_var.get().strip() or profile.username
            
            # Se mudou versão ou mod loader, marcar como não instalado
            if profile.mc_version != old_version or profile.mod_loader != old_loader:
                profile.installed = False
                # Limpar diretório do jogo antigo se existir
                import shutil
                game_dir = Path(profile.game_directory)
                if game_dir.exists():
                    try:
                        shutil.rmtree(game_dir)
                    except Exception as e:
                        print(f"[TITAN] Aviso ao limpar diretorio: {e}")
            
            self.save_profiles()
            dialog.destroy()
            
            if self.notification_manager:
                self.notification_manager.show("Atualizado", f"Perfil '{profile.name}' atualizado!", "success")
            
            # Atualizar a view atual
            if self.current_view == "home":
                self.show_home()
            elif self.current_view == "profiles":
                self.show_profiles()
        
        tk.Button(dialog, text="SALVAR ALTERACOES", command=save_changes,
                  bg='#4a9eff', fg='white', font=("Helvetica", 12, "bold"),
                  pady=12, bd=0, cursor='hand2', activebackground='#357abd').pack(fill='x', padx=20, pady=30)

    def delete_profile(self, profile):
        """Excluir perfil"""
        result = messagebox.askyesnocancel(
            "Confirmar Exclusao",
            f"Excluir perfil '{profile.name}'?\n\n"
            f"Sim = Excluir perfil E arquivos do jogo\n"
            f"Nao = Excluir apenas o perfil (manter arquivos)\n"
            f"Cancelar = Nao excluir nada"
        )
        
        if result is None:  # Cancelar
            return
        
        if result:  # Sim - deletar tudo
            import shutil
            game_dir = Path(profile.game_directory)
            if game_dir.exists():
                try:
                    shutil.rmtree(game_dir)
                except Exception as e:
                    print(f"[TITAN] Erro ao remover arquivos: {e}")
        
        del self.profiles[profile.id]
        self.save_profiles()
        
        if self.notification_manager:
            self.notification_manager.show("Excluido", f"Perfil '{profile.name}' removido", "info")
        
        self.show_profiles()

    def install_minecraft(self, profile):
        """Instala Minecraft para o perfil"""
        if not mll:
            messagebox.showerror("Erro", "minecraft_launcher_lib nao disponivel!")
            return
        
        # Verificar Java
        java_path = JavaManager.find_java()
        if not java_path:
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
                
                callback = {
                    'setMax': progress.set_max,
                    'setProgress': progress.set_progress
                }
                
                if profile.mod_loader == "forge":
                    self.set_status(f"Instalando Forge para {profile.mc_version}...")
                    progress.set_status(f"Buscando Forge para {profile.mc_version}...")
                    
                    # Encontrar versão do Forge
                    forge_version = mll.forge.find_forge_version(profile.mc_version)
                    if not forge_version:
                        raise Exception(f"Forge nao disponivel para Minecraft {profile.mc_version}")
                    
                    if not mll.forge.supports_automatic_install(forge_version):
                        raise Exception(f"Forge {forge_version} nao suporta instalacao automatica")
                    
                    progress.set_status(f"Instalando Forge {forge_version}...")
                    
                    # Instalar Forge (instala vanilla + forge)
                    mll.forge.install_forge_version(
                        forge_version,
                        str(path),
                        callback=callback,
                        java=java_path
                    )
                    
                    # Salvar o version ID do forge para usar no launch
                    profile.loader_version = mll.forge.forge_to_installed_version(forge_version)
                    
                elif profile.mod_loader == "fabric":
                    self.set_status(f"Instalando Fabric para {profile.mc_version}...")
                    progress.set_status(f"Instalando Fabric para {profile.mc_version}...")
                    
                    # Instalar Fabric
                    mll.fabric.install_fabric(
                        profile.mc_version,
                        str(path),
                        callback=callback,
                        java=java_path
                    )
                    
                    # Fabric version ID format
                    loader_ver = mll.fabric.get_latest_loader_version()
                    profile.loader_version = f"fabric-loader-{loader_ver}-{profile.mc_version}"
                    
                else:
                    # Vanilla
                    self.set_status(f"Instalando {profile.mc_version}...")
                    progress.set_status(f"Instalando Minecraft {profile.mc_version}...")
                    
                    mll.install.install_minecraft_version(
                        profile.mc_version,
                        str(path),
                        callback=callback
                    )
                    profile.loader_version = profile.mc_version
                
                profile.installed = True
                self.save_profiles()
                
                progress.close()
                self.root.after(0, lambda: messagebox.showinfo("Sucesso", f"{profile.name} instalado com sucesso!"))
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
            
            # Usar loader_version se disponível (contém o ID correto do Forge/Fabric)
            version_id = profile.loader_version if profile.loader_version and profile.loader_version != "latest" else profile.mc_version
            command = mll.command.get_minecraft_command(
                version_id,
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
