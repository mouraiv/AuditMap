import tkinter as tk
from tkinter import ttk
import threading

class LoadingSpinner(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        
        # Configuração do frame com fundo semi-transparente
        self.configure(bg='#000000', bd=1, highlightthickness=0)
        self.place(relx=0.5, rely=0.5, anchor='center')
        self.pack_propagate(False)
        self.configure(width=200, height=50)
        
        # Frame interno branco
        content_frame = tk.Frame(self, bg='#ffffff', padx=0, pady=3)
        content_frame.pack(expand=True, fill='both')
        
        # Label
        tk.Label(
            content_frame,
            text="Consultando API ...",
            bg='#ffffff',
            font=('Helvetica', 8, 'italic', 'bold')
        ).pack()

        # Spinner (barra de progresso indeterminada)
        self.spinner = ttk.Progressbar(
            content_frame,
            mode='indeterminate',
            length=100
        )
        self.spinner.pack(pady=(0, 3))
        
        # Controle de estado
        self.is_running = False
        
        # Esconde inicialmente
        self.place_forget()

    def show(self):
        """Mostra o spinner"""
        if not self.is_running:
            self.is_running = True
            self.lift()
            self.place(relx=0.5, rely=0.5, anchor='center')
            self.spinner.start(10)

    def hide(self):
        """Esconde o spinner"""
        if self.is_running:
            self.is_running = False
            self.spinner.stop()
            self.place_forget()

    def run_with_spinner(self, target_func, args=(), kwargs={}, callback=None):
        """Executa uma função com o spinner ativo"""
        def wrapper():
            try:
                self.parent.after(0, self.show)
                result = target_func(*args, **kwargs)
                if callback:
                    self.parent.after(0, lambda: callback(result))
            except Exception as e:
                print(f"Erro na operação: {str(e)}")
            finally:
                self.parent.after(0, self.hide)
        
        threading.Thread(target=wrapper, daemon=True).start()