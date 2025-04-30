import tkinter as tk
from tkinter import ttk, messagebox
import os
from ui.home_frame import HomeFrame
from ui.import_frame import ImportFrame
from ui.validation_frame import ValidationFrame
from ui.correction_frame import CorrectionFrame
from database import Database

class AuditMapApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("AuditMap - Verificação Inteligente de Endereços")
        self.geometry("1024x768")
        self.resizable(True, True)
        
        # Configuração do banco de dados
        self.db = Database()
        self.db.initialize_db()
        
        # Container principal
        self.container = tk.Frame(self)
        self.container.pack(side="top", fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)
        
        # Dicionário de frames
        self.frames = {}
        
        # Criação dos frames
        for F in (HomeFrame, ImportFrame, ValidationFrame, CorrectionFrame):
            frame = F(self.container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        
        # Mostrar o frame inicial
        self.show_frame(HomeFrame)
        
        # Configuração do menu
        self.create_menu()
    
    def create_menu(self):
        menubar = tk.Menu(self)
        
        # Menu Arquivo
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Voltar para Home", command=lambda: self.show_frame(HomeFrame))
        file_menu.add_separator()
        file_menu.add_command(label="Sair", command=self.quit)
        menubar.add_cascade(label="Arquivo", menu=file_menu)
        
        # Menu Ajuda
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="Sobre", command=self.show_about)
        menubar.add_cascade(label="Ajuda", menu=help_menu)
        
        self.config(menu=menubar)
    
    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()
        frame.update_data()
    
    def show_about(self):
        messagebox.showinfo("Sobre", "AuditMap\nVersão 1.0\n\nSistema de verificação inteligente de endereços e surveys de campo.")
    
    def on_closing(self):
        if messagebox.askokcancel("Sair", "Deseja realmente sair?"):
            self.db.close()
            self.destroy()

if __name__ == "__main__":
    app = AuditMapApp()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()