import tkinter as tk
from tkinter import ttk, messagebox
from ui.home_frame import HomeFrame
from ui.import_frame import ImportFrame
from ui.validation_frame import ValidationFrame
from ui.correction_frame import CorrectionFrame
from database import Database

class AuditMapApp(tk.Tk):
    def __init__(self):
        super().__init__()
        
        # Configurações básicas da janela principal
        self.title("AuditMap - Verificação Inteligente de Endereços")
        self.geometry("1024x768")
        self.resizable(True, True)
        
        # Configuração do banco de dados
        self.db = Database()
        self.db.initialize_db()
        
        # Definição de constantes para os nomes dos frames
        self.HOME_FRAME = 'HomeFrame'
        self.IMPORT_FRAME = 'ImportFrame'
        self.VALIDATION_FRAME = 'ValidationFrame'
        self.CORRECTION_FRAME = 'CorrectionFrame'
        
        # Container principal para os frames
        self.container = tk.Frame(self)
        self.container.pack(side="top", fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)
        
        # Dicionário para armazenar os frames
        self.frames = {}
        
        # Criação e registro dos frames
        self._create_frames()
        
        # Mostrar o frame inicial
        self.show_frame(self.HOME_FRAME)
        
        # Configuração do menu
        self._create_menu()
        
        # Configurar ação ao fechar a janela
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def _create_frames(self):
        """Cria e registra todos os frames da aplicação"""
        frames = {
            self.HOME_FRAME: HomeFrame,
            self.IMPORT_FRAME: ImportFrame,
            self.VALIDATION_FRAME: ValidationFrame,
            self.CORRECTION_FRAME: CorrectionFrame
        }
        
        for frame_name, FrameClass in frames.items():
            frame = FrameClass(self.container, self)
            self.frames[frame_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")
    
    def _create_menu(self):
        """Configura a barra de menu principal"""
        menubar = tk.Menu(self)
        
        # Menu Arquivo
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(
            label="Voltar para Home",
            command=lambda: self.show_frame(self.HOME_FRAME))
        file_menu.add_separator()
        file_menu.add_command(label="Sair", command=self.quit)
        menubar.add_cascade(label="Arquivo", menu=file_menu)
        
        # Menu Ajuda
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="Sobre", command=self.show_about)
        menubar.add_cascade(label="Ajuda", menu=help_menu)
        
        self.config(menu=menubar)
    
    def show_frame(self, frame_name):
        """
        Mostra o frame especificado
        :param frame_name: Nome do frame a ser mostrado (usar as constantes definidas)
        """
        frame = self.frames[frame_name]
        frame.tkraise()
        frame.update_data()
    
    def show_about(self):
        """Exibe a caixa de diálogo 'Sobre'"""
        messagebox.showinfo(
            "Sobre",
            "AuditMap\nVersão 1.0\n\nSistema de verificação inteligente de endereços e surveys de campo."
        )
    
    def on_closing(self):
        """Ação executada ao tentar fechar a janela"""
        if messagebox.askokcancel("Sair", "Deseja realmente sair?"):
            self.db.close()
            self.destroy()

if __name__ == "__main__":
    app = AuditMapApp()
    app.mainloop()