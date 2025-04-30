import tkinter as tk
from tkinter import ttk

class ImportFrame(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        
        label = tk.Label(self, text="Tela de Importação", font=('Helvetica', 18))
        label.pack(pady=20)
        
        back_btn = tk.Button(self, text="Voltar", command=lambda: controller.show_frame('HomeFrame'))
        back_btn.pack()
    
    def update_data(self):
        pass