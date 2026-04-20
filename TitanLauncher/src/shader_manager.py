#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TITAN LAUNCHER - Gerenciador de Shaders
Versão: 2.5.0
"""

import os
import json
import shutil
import zipfile
from pathlib import Path
from typing import List, Dict, Optional
import requests
from dataclasses import dataclass, asdict


@dataclass
class ShaderPack:
    """Representa um shader pack"""
    name: str
    version: str
    file_path: str
    enabled: bool = False
    description: str = ""
    author: str = ""
    minecraft_version: str = ""


class ShaderManager:
    """Gerenciador de shader packs"""
    
    POPULAR_SHADERS = {
        "BSL Shaders": {
            "description": "Shaders balanceados e otimizados",
            "versions": ["1.20.1", "1.19.4", "1.18.2", "1.16.5"],
            "category": "performance"
        },
        "Complementary Shaders": {
            "description": "Shaders realistas e detalhados",
            "versions": ["1.20.1", "1.19.4"],
            "category": "visual"
        },
        "Sildur's Vibrant Shaders": {
            "description": "Cores vibrantes e bonitas",
            "versions": ["1.20.1", "1.19.4", "1.18.2", "1.16.5", "1.12.2"],
            "category": "vibrant"
        },
        "SEUS PTGI": {
            "description": "Path-tracing ultra realista",
            "versions": ["1.20.1", "1.16.5"],
            "category": "ultra"
        },
        "Continuum Shaders": {
            "description": "Realismo fotográfico",
            "versions": ["1.20.1", "1.16.5"],
            "category": "ultra"
        },
        "Chocapic13": {
            "description": "Alto desempenho com boa qualidade",
            "versions": ["1.20.1", "1.19.4", "1.18.2", "1.16.5"],
            "category": "performance"
        },
        "Sonic Ether's Unbelievable Shaders": {
            "description": "Shaders clássicos e confiáveis",
            "versions": ["1.20.1", "1.16.5", "1.12.2"],
            "category": "classic"
        },
        "MakeUp Ultra Fast": {
            "description": "Otimizado para PCs fracos",
            "versions": ["1.20.1", "1.19.4", "1.18.2"],
            "category": "lite"
        },
        "Vanilla Plus Shaders": {
            "description": "Melhora sutil do vanilla",
            "versions": ["1.20.1", "1.19.4"],
            "category": "lite"
        },
        "ProjectLUMA": {
            "description": "Equilíbrio perfeito",
            "versions": ["1.20.1", "1.19.4"],
            "category": "balanced"
        }
    }
    
    def __init__(self, minecraft_dir: Path):
        self.minecraft_dir = minecraft_dir
        self.shaderpacks_dir = minecraft_dir / "shaderpacks"
        self.shaderpacks_dir.mkdir(parents=True, exist_ok=True)
        
        self.installed_shaders: List[ShaderPack] = []
        self.load_installed_shaders()
    
    def load_installed_shaders(self):
        """Carrega shaders instalados"""
        self.installed_shaders.clear()
        
        if not self.shaderpacks_dir.exists():
            return
        
        for file in self.shaderpacks_dir.iterdir():
            if file.suffix == '.zip':
                shader = ShaderPack(
                    name=file.stem,
                    version="unknown",
                    file_path=str(file),
                    enabled=False
                )
                self.installed_shaders.append(shader)
    
    def install_shader(self, shader_path: str) -> bool:
        """Instala um shader pack"""
        try:
            source = Path(shader_path)
            if not source.exists():
                return False
            
            # Copiar para pasta de shaders
            dest = self.shaderpacks_dir / source.name
            shutil.copy2(source, dest)
            
            # Recarregar lista
            self.load_installed_shaders()
            return True
            
        except Exception as e:
            print(f"[SHADERS] Erro ao instalar: {e}")
            return False
    
    def uninstall_shader(self, shader_name: str) -> bool:
        """Desinstala um shader pack"""
        try:
            for shader in self.installed_shaders:
                if shader.name == shader_name:
                    shader_file = Path(shader.file_path)
                    if shader_file.exists():
                        shader_file.unlink()
                    self.installed_shaders.remove(shader)
                    return True
            return False
            
        except Exception as e:
            print(f"[SHADERS] Erro ao desinstalar: {e}")
            return False
    
    def enable_shader(self, shader_name: str):
        """Habilita um shader (configura no options.txt)"""
        try:
            options_file = self.minecraft_dir / "optionsshaders.txt"
            
            # Criar arquivo se não existir
            if not options_file.exists():
                with open(options_file, 'w') as f:
                    f.write(f"shaderPack={shader_name}.zip\n")
            else:
                # Atualizar arquivo existente
                with open(options_file, 'r') as f:
                    lines = f.readlines()
                
                found = False
                for i, line in enumerate(lines):
                    if line.startswith('shaderPack='):
                        lines[i] = f"shaderPack={shader_name}.zip\n"
                        found = True
                        break
                
                if not found:
                    lines.append(f"shaderPack={shader_name}.zip\n")
                
                with open(options_file, 'w') as f:
                    f.writelines(lines)
            
            # Atualizar estado
            for shader in self.installed_shaders:
                shader.enabled = (shader.name == shader_name)
            
            return True
            
        except Exception as e:
            print(f"[SHADERS] Erro ao habilitar: {e}")
            return False
    
    def disable_shaders(self):
        """Desabilita todos os shaders"""
        try:
            options_file = self.minecraft_dir / "optionsshaders.txt"
            
            if options_file.exists():
                with open(options_file, 'r') as f:
                    lines = f.readlines()
                
                for i, line in enumerate(lines):
                    if line.startswith('shaderPack='):
                        lines[i] = "shaderPack=\n"
                        break
                
                with open(options_file, 'w') as f:
                    f.writelines(lines)
            
            # Atualizar estado
            for shader in self.installed_shaders:
                shader.enabled = False
            
            return True
            
        except Exception as e:
            print(f"[SHADERS] Erro ao desabilitar: {e}")
            return False
    
    def get_shader_recommendations(self, minecraft_version: str, category: str = "all"):
        """Retorna recomendações de shaders"""
        recommendations = []
        
        for name, info in self.POPULAR_SHADERS.items():
            if category != "all" and info["category"] != category:
                continue
            
            if minecraft_version in info["versions"]:
                recommendations.append({
                    "name": name,
                    "description": info["description"],
                    "category": info["category"]
                })
        
        return recommendations
    
    def check_optifine_or_iris(self) -> Optional[str]:
        """Verifica se OptiFine ou Iris está instalado"""
        # Verificar mods
        mods_dir = self.minecraft_dir / "mods"
        if not mods_dir.exists():
            return None
        
        for mod_file in mods_dir.iterdir():
            name_lower = mod_file.name.lower()
            if 'optifine' in name_lower:
                return "OptiFine"
            elif 'iris' in name_lower:
                return "Iris"
        
        return None
    
    def get_installed_count(self) -> int:
        """Retorna número de shaders instalados"""
        return len(self.installed_shaders)
    
    def get_enabled_shader(self) -> Optional[ShaderPack]:
        """Retorna o shader atualmente habilitado"""
        for shader in self.installed_shaders:
            if shader.enabled:
                return shader
        return None
