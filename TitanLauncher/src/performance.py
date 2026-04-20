#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TITAN LAUNCHER - Monitor de Performance
Versão: 2.5.0
"""

import tkinter as tk
from tkinter import ttk
import threading
import time
from typing import Optional

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False


class PerformanceMonitor:
    """Monitor de performance em tempo real"""
    
    def __init__(self, parent):
        self.parent = parent
        self.monitoring = False
        self.monitor_thread = None
        self.monitor_window = None
        
        self.cpu_usage = 0
        self.ram_usage = 0
        self.ram_total = 0
        self.ram_available = 0
        self.process_count = 0
        
    def start_monitoring(self):
        """Inicia o monitoramento"""
        if not PSUTIL_AVAILABLE:
            return
        
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
    
    def stop_monitoring(self):
        """Para o monitoramento"""
        self.monitoring = False
    
    def _monitor_loop(self):
        """Loop de monitoramento"""
        while self.monitoring:
            try:
                self.cpu_usage = psutil.cpu_percent(interval=1)
                
                mem = psutil.virtual_memory()
                self.ram_usage = mem.percent
                self.ram_total = mem.total / (1024 ** 3)  # GB
                self.ram_available = mem.available / (1024 ** 3)  # GB
                
                self.process_count = len(psutil.pids())
                
            except Exception as e:
                print(f"[MONITOR] Erro: {e}")
            
            time.sleep(2)
    
    def show_monitor_window(self):
        """Mostra janela de monitoramento"""
        if self.monitor_window is not None:
            self.monitor_window.lift()
            return
        
        self.monitor_window = tk.Toplevel(self.parent)
        self.monitor_window.title("Monitor de Performance")
        self.monitor_window.geometry("400x300")
        self.monitor_window.configure(bg='#2b2b2b')
        
        # Iniciar monitoramento se não estiver
        if not self.monitoring:
            self.start_monitoring()
        
        # Frame principal
        main_frame = tk.Frame(self.monitor_window, bg='#2b2b2b')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # CPU
        tk.Label(
            main_frame,
            text="CPU",
            font=("Helvetica", 12, "bold"),
            bg='#2b2b2b',
            fg='white'
        ).pack(anchor='w')
        
        self.cpu_progress = ttk.Progressbar(
            main_frame,
            length=350,
            mode='determinate'
        )
        self.cpu_progress.pack(pady=5)
        
        self.cpu_label = tk.Label(
            main_frame,
            text="0%",
            font=("Helvetica", 10),
            bg='#2b2b2b',
            fg='#aaaaaa'
        )
        self.cpu_label.pack(anchor='w', pady=(0, 20))
        
        # RAM
        tk.Label(
            main_frame,
            text="RAM",
            font=("Helvetica", 12, "bold"),
            bg='#2b2b2b',
            fg='white'
        ).pack(anchor='w')
        
        self.ram_progress = ttk.Progressbar(
            main_frame,
            length=350,
            mode='determinate'
        )
        self.ram_progress.pack(pady=5)
        
        self.ram_label = tk.Label(
            main_frame,
            text="0 GB / 0 GB",
            font=("Helvetica", 10),
            bg='#2b2b2b',
            fg='#aaaaaa'
        )
        self.ram_label.pack(anchor='w', pady=(0, 20))
        
        # Processos
        self.process_label = tk.Label(
            main_frame,
            text="Processos: 0",
            font=("Helvetica", 10),
            bg='#2b2b2b',
            fg='#aaaaaa'
        )
        self.process_label.pack(anchor='w')
        
        # Atualizar display
        self._update_display()
        
        # Cleanup ao fechar
        self.monitor_window.protocol("WM_DELETE_WINDOW", self._on_close_monitor)
    
    def _update_display(self):
        """Atualiza o display do monitor"""
        if self.monitor_window is None or not self.monitor_window.winfo_exists():
            return
        
        try:
            # CPU
            self.cpu_progress['value'] = self.cpu_usage
            self.cpu_label.config(text=f"{self.cpu_usage:.1f}%")
            
            # RAM
            self.ram_progress['value'] = self.ram_usage
            used_gb = self.ram_total - self.ram_available
            self.ram_label.config(
                text=f"{used_gb:.1f} GB / {self.ram_total:.1f} GB ({self.ram_usage:.1f}%)"
            )
            
            # Processos
            self.process_label.config(text=f"Processos: {self.process_count}")
            
        except Exception as e:
            print(f"[MONITOR] Erro ao atualizar display: {e}")
        
        # Agendar próxima atualização
        if self.monitor_window and self.monitor_window.winfo_exists():
            self.monitor_window.after(1000, self._update_display)
    
    def _on_close_monitor(self):
        """Callback ao fechar janela de monitoramento"""
        self.monitor_window.destroy()
        self.monitor_window = None
    
    def get_stats(self):
        """Retorna estatísticas atuais"""
        return {
            'cpu': self.cpu_usage,
            'ram_percent': self.ram_usage,
            'ram_total': self.ram_total,
            'ram_available': self.ram_available,
            'processes': self.process_count
        }


class PerformanceWidget:
    """Widget compacto de performance para barra de status"""
    
    def __init__(self, parent, monitor: PerformanceMonitor):
        self.parent = parent
        self.monitor = monitor
        
        self.frame = tk.Frame(parent, bg='#2b2b2b')
        
        # CPU
        self.cpu_label = tk.Label(
            self.frame,
            text="CPU: --%",
            font=("Helvetica", 9),
            bg='#2b2b2b',
            fg='#aaaaaa'
        )
        self.cpu_label.pack(side='left', padx=5)
        
        # RAM
        self.ram_label = tk.Label(
            self.frame,
            text="RAM: --%",
            font=("Helvetica", 9),
            bg='#2b2b2b',
            fg='#aaaaaa'
        )
        self.ram_label.pack(side='left', padx=5)
        
        # Atualizar
        self._update()
    
    def _update(self):
        """Atualiza os valores"""
        stats = self.monitor.get_stats()
        
        self.cpu_label.config(text=f"CPU: {stats['cpu']:.0f}%")
        self.ram_label.config(text=f"RAM: {stats['ram_percent']:.0f}%")
        
        self.parent.after(2000, self._update)
    
    def pack(self, **kwargs):
        """Pack do frame"""
        self.frame.pack(**kwargs)
