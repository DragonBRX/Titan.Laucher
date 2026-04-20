#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TITAN LAUNCHER - Utilitários
Versão: 2.5.0
"""

import os
import sys
import hashlib
import platform
import subprocess
from pathlib import Path
from typing import Optional, List, Dict
import json


class SystemInfo:
    """Informações do sistema"""
    
    @staticmethod
    def get_os_info() -> Dict:
        """Retorna informações do sistema operacional"""
        return {
            'system': platform.system(),
            'release': platform.release(),
            'version': platform.version(),
            'machine': platform.machine(),
            'processor': platform.processor()
        }
    
    @staticmethod
    def get_java_version() -> Optional[str]:
        """Detecta versão do Java instalada"""
        try:
            result = subprocess.run(
                ['java', '-version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            # Java imprime versão no stderr
            output = result.stderr
            
            # Extrair número da versão
            for line in output.split('\n'):
                if 'version' in line.lower():
                    # Exemplo: java version "17.0.5"
                    if '"' in line:
                        version = line.split('"')[1]
                        return version
            
            return None
            
        except Exception as e:
            print(f"[SYSTEM] Erro ao detectar Java: {e}")
            return None
    
    @staticmethod
    def find_java_installations() -> List[Dict]:
        """Encontra instalações do Java no sistema"""
        java_paths = []
        
        system = platform.system()
        
        # Locais comuns de instalação
        search_paths = []
        
        if system == "Linux":
            search_paths = [
                Path("/usr/lib/jvm"),
                Path("/usr/java"),
                Path.home() / ".jdks"
            ]
        elif system == "Windows":
            search_paths = [
                Path("C:/Program Files/Java"),
                Path("C:/Program Files/Eclipse Adoptium"),
                Path("C:/Program Files/Microsoft")
            ]
        elif system == "Darwin":  # macOS
            search_paths = [
                Path("/Library/Java/JavaVirtualMachines"),
                Path.home() / "Library/Java/JavaVirtualMachines"
            ]
        
        # Buscar em cada caminho
        for search_path in search_paths:
            if not search_path.exists():
                continue
            
            try:
                for item in search_path.iterdir():
                    if item.is_dir():
                        # Procurar executável java
                        java_bin = None
                        
                        if system == "Windows":
                            java_bin = item / "bin" / "java.exe"
                        else:
                            java_bin = item / "bin" / "java"
                        
                        if java_bin.exists():
                            java_paths.append({
                                'path': str(java_bin),
                                'name': item.name,
                                'location': str(item)
                            })
            except PermissionError:
                continue
        
        return java_paths
    
    @staticmethod
    def get_recommended_ram() -> int:
        """Retorna quantidade recomendada de RAM em GB"""
        try:
            import psutil
            total_ram = psutil.virtual_memory().total / (1024 ** 3)  # GB
            
            # Recomendar 50% da RAM total, mínimo 2GB, máximo 8GB
            recommended = max(2, min(8, int(total_ram * 0.5)))
            return recommended
        except:
            return 4  # Padrão


class FileUtils:
    """Utilitários para arquivos"""
    
    @staticmethod
    def calculate_md5(file_path: Path) -> str:
        """Calcula hash MD5 de um arquivo"""
        md5_hash = hashlib.md5()
        
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                md5_hash.update(chunk)
        
        return md5_hash.hexdigest()
    
    @staticmethod
    def get_directory_size(path: Path) -> int:
        """Retorna tamanho de um diretório em bytes"""
        total = 0
        
        try:
            for entry in path.rglob('*'):
                if entry.is_file():
                    total += entry.stat().st_size
        except Exception as e:
            print(f"[FILEUTILS] Erro ao calcular tamanho: {e}")
        
        return total
    
    @staticmethod
    def format_size(size_bytes: int) -> str:
        """Formata tamanho em bytes para string legível"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} PB"
    
    @staticmethod
    def safe_delete(path: Path) -> bool:
        """Deleta arquivo ou diretório com segurança"""
        try:
            if path.is_file():
                path.unlink()
            elif path.is_dir():
                import shutil
                shutil.rmtree(path)
            return True
        except Exception as e:
            print(f"[FILEUTILS] Erro ao deletar: {e}")
            return False


class ConfigManager:
    """Gerenciador de configurações avançadas"""
    
    def __init__(self, config_path: Path):
        self.config_path = config_path
        self.config = self.load()
    
    def load(self) -> Dict:
        """Carrega configurações"""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    return json.load(f)
            except:
                pass
        
        # Configurações padrão
        return {
            'theme': 'dark',
            'language': 'pt_BR',
            'auto_update': True,
            'show_notifications': True,
            'performance_monitoring': True,
            'auto_backup': True,
            'backup_interval_days': 7,
            'max_backups': 5,
            'download_threads': 4,
            'show_snapshots': False,
            'show_old_versions': False,
            'compact_mode': False,
            'remember_window_size': True,
            'window_width': 1100,
            'window_height': 700,
            'check_updates_on_start': True,
            'discord_rpc': False,
            'java_auto_detect': True,
            'preferred_java_path': None,
            'custom_jvm_args_global': "",
            'enable_experimental_features': False
        }
    
    def save(self):
        """Salva configurações"""
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"[CONFIG] Erro ao salvar: {e}")
    
    def get(self, key: str, default=None):
        """Obtém uma configuração"""
        return self.config.get(key, default)
    
    def set(self, key: str, value):
        """Define uma configuração"""
        self.config[key] = value
        self.save()
    
    def reset_to_defaults(self):
        """Reseta para configurações padrão"""
        self.config = self.load.__func__(self)
        self.save()


class URLHandler:
    """Manipulador de URLs customizadas (titan://)"""
    
    @staticmethod
    def register_protocol():
        """Registra protocolo titan:// no sistema"""
        system = platform.system()
        
        if system == "Linux":
            # Criar arquivo .desktop
            desktop_file = Path.home() / ".local/share/applications/titan-launcher.desktop"
            desktop_file.parent.mkdir(parents=True, exist_ok=True)
            
            launcher_path = Path(__file__).parent.parent / "src" / "main.py"
            
            content = f"""[Desktop Entry]
Type=Application
Name=Titan Launcher
Exec=python3 "{launcher_path}" %u
MimeType=x-scheme-handler/titan;
NoDisplay=true
"""
            
            with open(desktop_file, 'w') as f:
                f.write(content)
            
            # Atualizar banco de dados MIME
            subprocess.run(['update-desktop-database', str(desktop_file.parent)])
        
        elif system == "Windows":
            # Adicionar chave no registro (requer admin)
            pass
    
    @staticmethod
    def parse_url(url: str) -> Optional[Dict]:
        """
        Parse de URL titan://
        
        Exemplos:
        - titan://play/profile_id
        - titan://install/version/forge
        - titan://import/profile_url
        """
        if not url.startswith('titan://'):
            return None
        
        url = url.replace('titan://', '')
        parts = url.split('/')
        
        if len(parts) < 1:
            return None
        
        action = parts[0]
        params = parts[1:] if len(parts) > 1 else []
        
        return {
            'action': action,
            'params': params
        }


class QuickActions:
    """Ações rápidas e atalhos"""
    
    @staticmethod
    def open_minecraft_folder(game_dir: Path):
        """Abre pasta do Minecraft no explorador"""
        system = platform.system()
        
        if system == "Windows":
            os.startfile(game_dir)
        elif system == "Darwin":  # macOS
            subprocess.run(['open', str(game_dir)])
        else:  # Linux
            subprocess.run(['xdg-open', str(game_dir)])
    
    @staticmethod
    def open_logs_folder(game_dir: Path):
        """Abre pasta de logs"""
        logs_dir = game_dir / "logs"
        if logs_dir.exists():
            QuickActions.open_minecraft_folder(logs_dir)
    
    @staticmethod
    def open_screenshots_folder(game_dir: Path):
        """Abre pasta de screenshots"""
        screenshots_dir = game_dir / "screenshots"
        if screenshots_dir.exists():
            QuickActions.open_minecraft_folder(screenshots_dir)
    
    @staticmethod
    def clear_cache(game_dir: Path) -> bool:
        """Limpa cache do Minecraft"""
        try:
            cache_dirs = [
                game_dir / "assets" / "cache",
                game_dir / "libraries" / "cache"
            ]
            
            for cache_dir in cache_dirs:
                if cache_dir.exists():
                    import shutil
                    shutil.rmtree(cache_dir)
            
            return True
        except Exception as e:
            print(f"[QUICK] Erro ao limpar cache: {e}")
            return False
