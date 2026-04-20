#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TITAN LAUNCHER - Sistema de Notificações
Versão: 2.5.0
"""

import tkinter as tk
from datetime import datetime
from typing import List, Callable


class Notification:
    """Classe de notificação"""
    
    def __init__(self, title, message, type="info", duration=3000):
        self.title = title
        self.message = message
        self.type = type  # info, success, warning, error
        self.duration = duration
        self.timestamp = datetime.now()


class NotificationManager:
    """Gerenciador de notificações"""
    
    def __init__(self, parent):
        self.parent = parent
        self.notifications: List[Notification] = []
        self.notification_widgets = []
        self.max_notifications = 5
        self.notification_container = None
        
    def create_container(self):
        """Cria o container de notificações"""
        if self.notification_container is None:
            self.notification_container = tk.Frame(
                self.parent,
                bg='#2b2b2b'  # Usar cor sólida ao invés de transparent
            )
            self.notification_container.place(
                relx=1.0, 
                rely=1.0, 
                anchor='se',
                x=-20,
                y=-20
            )
    
    def show(self, title, message, type="info", duration=3000):
        """Mostra uma notificação"""
        self.create_container()
        
        notification = Notification(title, message, type, duration)
        self.notifications.append(notification)
        
        # Cores por tipo
        colors = {
            "info": ("#2196f3", "#ffffff"),
            "success": ("#4caf50", "#ffffff"),
            "warning": ("#ff9800", "#000000"),
            "error": ("#f44336", "#ffffff"),
        }
        
        bg_color, fg_color = colors.get(type, colors["info"])
        
        # Criar widget de notificação
        notif_frame = tk.Frame(
            self.notification_container,
            bg=bg_color,
            highlightbackground="#ffffff",
            highlightthickness=1,
            padx=15,
            pady=10
        )
        notif_frame.pack(side='bottom', pady=5, fill='x')
        
        # Título
        title_label = tk.Label(
            notif_frame,
            text=title,
            font=("Helvetica", 10, "bold"),
            bg=bg_color,
            fg=fg_color
        )
        title_label.pack(anchor='w')
        
        # Mensagem
        msg_label = tk.Label(
            notif_frame,
            text=message,
            font=("Helvetica", 9),
            bg=bg_color,
            fg=fg_color,
            wraplength=250,
            justify='left'
        )
        msg_label.pack(anchor='w')
        
        self.notification_widgets.append(notif_frame)
        
        # Auto-remover
        if duration > 0:
            self.parent.after(duration, lambda: self._remove_notification(notif_frame))
        
        # Limitar número de notificações
        while len(self.notification_widgets) > self.max_notifications:
            oldest = self.notification_widgets.pop(0)
            oldest.destroy()
    
    def _remove_notification(self, widget):
        """Remove uma notificação"""
        try:
            if widget in self.notification_widgets:
                self.notification_widgets.remove(widget)
            widget.destroy()
        except:
            pass
    
    def clear_all(self):
        """Limpa todas as notificações"""
        for widget in self.notification_widgets:
            widget.destroy()
        self.notification_widgets.clear()
        self.notifications.clear()


class ToastNotification:
    """Notificação estilo Toast (mais discreta)"""
    
    @staticmethod
    def show(parent, message, duration=2000, bg="#333333", fg="#ffffff"):
        """Mostra uma notificação toast"""
        toast = tk.Toplevel(parent)
        toast.withdraw()
        toast.overrideredirect(True)
        toast.configure(bg=bg)
        
        label = tk.Label(
            toast,
            text=message,
            bg=bg,
            fg=fg,
            font=("Helvetica", 9),
            padx=20,
            pady=10
        )
        label.pack()
        
        # Posicionar no centro inferior
        toast.update_idletasks()
        width = toast.winfo_width()
        height = toast.winfo_height()
        screen_width = parent.winfo_screenwidth()
        screen_height = parent.winfo_screenheight()
        
        x = (screen_width - width) // 2
        y = screen_height - height - 100
        
        toast.geometry(f"+{x}+{y}")
        toast.deiconify()
        
        # Fade out e destruir
        def fade_out(alpha=1.0):
            if alpha > 0:
                toast.attributes('-alpha', alpha)
                parent.after(50, lambda: fade_out(alpha - 0.1))
            else:
                toast.destroy()
        
        parent.after(duration, lambda: fade_out())
