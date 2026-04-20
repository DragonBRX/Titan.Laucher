#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TITAN LAUNCHER - Exportador/Importador de Perfis
Versão: 2.5.0
"""

import json
import zipfile
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import asdict


class ProfileExporter:
    """Exportador de perfis"""
    
    @staticmethod
    def export_profile(profile, export_path: str, include_mods: bool = True,
                      include_saves: bool = False, include_config: bool = True):
        """
        Exporta um perfil para um arquivo .titanprofile
        
        Args:
            profile: GameProfile a ser exportado
            export_path: Caminho do arquivo de destino
            include_mods: Incluir pasta de mods
            include_saves: Incluir mundos salvos
            include_config: Incluir configurações do Minecraft
        """
        try:
            export_file = Path(export_path)
            game_dir = Path(profile.game_directory)
            
            # Criar arquivo ZIP
            with zipfile.ZipFile(export_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Adicionar metadados do perfil
                profile_data = asdict(profile)
                profile_data['export_date'] = datetime.now().isoformat()
                profile_data['export_version'] = '2.5.0'
                
                zipf.writestr('profile.json', json.dumps(profile_data, indent=2))
                
                # Adicionar README
                readme = f"""
TITAN LAUNCHER - Perfil Exportado
==================================

Perfil: {profile.name}
Versão do Minecraft: {profile.mc_version}
Mod Loader: {profile.mod_loader}
Exportado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}

Este arquivo pode ser importado no Titan Launcher.

Conteúdo:
- Configurações do perfil: ✓
- Mods: {'✓' if include_mods else '✗'}
- Mundos: {'✓' if include_saves else '✗'}
- Configs: {'✓' if include_config else '✗'}
"""
                zipf.writestr('README.txt', readme)
                
                # Adicionar mods se solicitado
                if include_mods:
                    mods_dir = game_dir / "mods"
                    if mods_dir.exists():
                        for mod_file in mods_dir.iterdir():
                            if mod_file.is_file():
                                arcname = f"mods/{mod_file.name}"
                                zipf.write(mod_file, arcname)
                
                # Adicionar saves se solicitado
                if include_saves:
                    saves_dir = game_dir / "saves"
                    if saves_dir.exists():
                        for save_folder in saves_dir.iterdir():
                            if save_folder.is_dir():
                                for root, dirs, files in save_folder.walk():
                                    for file in files:
                                        file_path = root / file
                                        arcname = f"saves/{save_folder.name}/{file_path.relative_to(saves_dir / save_folder.name)}"
                                        zipf.write(file_path, arcname)
                
                # Adicionar configs se solicitado
                if include_config:
                    config_files = [
                        "options.txt",
                        "optionsof.txt",
                        "optionsshaders.txt",
                        "servers.dat"
                    ]
                    
                    for config_file in config_files:
                        config_path = game_dir / config_file
                        if config_path.exists():
                            zipf.write(config_path, f"config/{config_file}")
            
            return True, f"Perfil exportado com sucesso!"
            
        except Exception as e:
            return False, f"Erro ao exportar: {str(e)}"
    
    @staticmethod
    def import_profile(import_path: str, minecraft_dir: Path, 
                      new_name: Optional[str] = None) -> tuple[bool, str, Optional[Dict]]:
        """
        Importa um perfil de um arquivo .titanprofile
        
        Returns:
            (sucesso, mensagem, dados_do_perfil)
        """
        try:
            import_file = Path(import_path)
            
            if not import_file.exists():
                return False, "Arquivo não encontrado", None
            
            # Ler arquivo ZIP
            with zipfile.ZipFile(import_file, 'r') as zipf:
                # Ler metadados
                profile_json = zipf.read('profile.json').decode('utf-8')
                profile_data = json.loads(profile_json)
                
                # Gerar novo nome se solicitado
                if new_name:
                    profile_data['name'] = new_name
                
                # Criar diretório do jogo
                game_dir = minecraft_dir / profile_data['name']
                game_dir.mkdir(parents=True, exist_ok=True)
                
                # Atualizar game_directory
                profile_data['game_directory'] = str(game_dir)
                
                # Extrair mods
                for file in zipf.namelist():
                    if file.startswith('mods/'):
                        zipf.extract(file, game_dir.parent)
                
                # Extrair saves
                for file in zipf.namelist():
                    if file.startswith('saves/'):
                        zipf.extract(file, game_dir.parent)
                
                # Extrair configs
                for file in zipf.namelist():
                    if file.startswith('config/'):
                        config_name = Path(file).name
                        zipf.extract(file, game_dir.parent)
                        # Mover para local correto
                        src = game_dir.parent / file
                        dst = game_dir / config_name
                        if src.exists():
                            shutil.move(str(src), str(dst))
                
                # Limpar pasta temporária de config
                temp_config = game_dir.parent / "config"
                if temp_config.exists():
                    shutil.rmtree(temp_config)
                
                # Marcar como não instalado (precisa instalar versão MC)
                profile_data['installed'] = False
                
                return True, "Perfil importado com sucesso!", profile_data
                
        except Exception as e:
            return False, f"Erro ao importar: {str(e)}", None
    
    @staticmethod
    def get_profile_info(import_path: str) -> Optional[Dict]:
        """Obtém informações de um arquivo de perfil sem importar"""
        try:
            import_file = Path(import_path)
            
            with zipfile.ZipFile(import_file, 'r') as zipf:
                profile_json = zipf.read('profile.json').decode('utf-8')
                profile_data = json.loads(profile_json)
                
                # Contar arquivos
                mods_count = sum(1 for f in zipf.namelist() if f.startswith('mods/'))
                saves_count = len(set(f.split('/')[1] for f in zipf.namelist() if f.startswith('saves/') and len(f.split('/')) > 2))
                
                return {
                    'name': profile_data.get('name'),
                    'mc_version': profile_data.get('mc_version'),
                    'mod_loader': profile_data.get('mod_loader'),
                    'ram_gb': profile_data.get('ram_gb'),
                    'export_date': profile_data.get('export_date'),
                    'mods_count': mods_count,
                    'saves_count': saves_count,
                    'has_config': any(f.startswith('config/') for f in zipf.namelist())
                }
                
        except Exception as e:
            print(f"[EXPORTER] Erro ao ler info: {e}")
            return None


class ProfileBackup:
    """Sistema de backup de perfis"""
    
    def __init__(self, backup_dir: Path):
        self.backup_dir = backup_dir
        self.backup_dir.mkdir(parents=True, exist_ok=True)
    
    def create_backup(self, profile, name: Optional[str] = None) -> tuple[bool, str]:
        """Cria um backup do perfil"""
        try:
            if name is None:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                name = f"{profile.name}_{timestamp}"
            
            backup_file = self.backup_dir / f"{name}.titanbackup"
            
            # Usar exportador
            success, msg = ProfileExporter.export_profile(
                profile,
                str(backup_file),
                include_mods=True,
                include_saves=True,
                include_config=True
            )
            
            if success:
                return True, f"Backup criado: {backup_file.name}"
            else:
                return False, msg
                
        except Exception as e:
            return False, f"Erro ao criar backup: {str(e)}"
    
    def list_backups(self, profile_name: Optional[str] = None) -> List[Dict]:
        """Lista backups disponíveis"""
        backups = []
        
        for backup_file in self.backup_dir.glob("*.titanbackup"):
            info = ProfileExporter.get_profile_info(str(backup_file))
            if info:
                if profile_name is None or info['name'] == profile_name:
                    info['backup_file'] = str(backup_file)
                    info['backup_name'] = backup_file.stem
                    info['backup_size'] = backup_file.stat().st_size / (1024 * 1024)  # MB
                    backups.append(info)
        
        return sorted(backups, key=lambda x: x.get('export_date', ''), reverse=True)
    
    def restore_backup(self, backup_path: str, minecraft_dir: Path) -> tuple[bool, str, Optional[Dict]]:
        """Restaura um backup"""
        return ProfileExporter.import_profile(backup_path, minecraft_dir)
    
    def delete_backup(self, backup_path: str) -> bool:
        """Deleta um backup"""
        try:
            backup_file = Path(backup_path)
            if backup_file.exists():
                backup_file.unlink()
                return True
            return False
        except Exception as e:
            print(f"[BACKUP] Erro ao deletar: {e}")
            return False
