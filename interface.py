import tkinter as tk
from tkinter import ttk
import json
from datetime import datetime
from banco import meusqldb
from clima import climinha
from dados_dispo import dispositivo
from indice_kp import IndiceKP
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from main import main

class Interface:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Monitoramento")
        self.root.geometry("1400x900")
        self.root.configure(bg="#f0f0f0")

        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        self.style.configure('Card.TFrame', background='white', relief='flat')
        self.style.configure('Title.TLabel', font=('Helvetica', 16, 'bold'), background='white')
        self.style.configure('Subtitle.TLabel', font=('Helvetica', 12), background='white')
        self.style.configure('Data.TLabel', font=('Helvetica', 10), background='white')
        self.style.configure('Treeview', font=('Helvetica', 10))
        self.style.configure('Treeview.Heading', font=('Helvetica', 10, 'bold'))
        
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(expand=True, fill='both', padx=20, pady=20)
        
        self.create_clima_tab()
        self.create_dispositivo_tab()
        self.create_kp_tab()
        
        self.update_data()
        
    def convert_kp_value(self, kp_str):
        try:
            kp_str = kp_str.replace('M', '').replace('Z', '')
            return float(kp_str)
        except (ValueError, TypeError):
            return 0.0  
        
    def create_card(self, parent, title):
        card = ttk.Frame(parent, style='Card.TFrame')
        card.pack(fill='x', padx=10, pady=5)
        
        title_label = ttk.Label(card, text=title, style='Title.TLabel')
        title_label.pack(anchor='w', padx=10, pady=5)
        
        return card
        
    def create_clima_tab(self):
        clima_frame = ttk.Frame(self.notebook)
        self.notebook.add(clima_frame, text='Clima')
        
        current_frame = ttk.Frame(clima_frame)
        current_frame.pack(fill='x', padx=10, pady=5)
        
        temp_card = self.create_card(current_frame, "Temperatura Atual")
        self.temp_label = ttk.Label(temp_card, text="--°C", style='Data.TLabel', font=('Helvetica', 24))
        self.temp_label.pack(padx=10, pady=5)
        
        vento_card = self.create_card(current_frame, "Condições do Vento")
        self.vento_label = ttk.Label(vento_card, text="Velocidade: -- km/h\nDireção: --°", style='Data.TLabel')
        self.vento_label.pack(padx=10, pady=5)
        
        data_frame = ttk.Frame(clima_frame)
        data_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        self.fig_temp = Figure(figsize=(6, 4), dpi=100)
        self.ax_temp = self.fig_temp.add_subplot(111)
        self.canvas_temp = FigureCanvasTkAgg(self.fig_temp, master=data_frame)
        self.canvas_temp.get_tk_widget().pack(side='left', fill='both', expand=True)
        
        table_frame = ttk.Frame(data_frame)
        table_frame.pack(side='right', fill='both', expand=True, padx=10)
        
        columns = ('Data', 'Temperatura', 'Vento', 'Direção')
        self.clima_tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=10)
        
        for col in columns:
            self.clima_tree.heading(col, text=col)
            self.clima_tree.column(col, width=100)
        
        scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=self.clima_tree.yview)
        self.clima_tree.configure(yscrollcommand=scrollbar.set)
        
        self.clima_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
    def create_dispositivo_tab(self):
        dispositivo_frame = ttk.Frame(self.notebook)
        self.notebook.add(dispositivo_frame, text='Dispositivo')
        
        info_frame = ttk.Frame(dispositivo_frame)
        info_frame.pack(fill='x', padx=10, pady=5)
        
        
        details_frame = ttk.Frame(dispositivo_frame)
        details_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        columns = ('Propriedade', 'Valor')
        self.dispo_tree = ttk.Treeview(details_frame, columns=columns, show='headings', height=10)
        
        for col in columns:
            self.dispo_tree.heading(col, text=col)
            self.dispo_tree.column(col, width=150)
        
        scrollbar = ttk.Scrollbar(details_frame, orient='vertical', command=self.dispo_tree.yview)
        self.dispo_tree.configure(yscrollcommand=scrollbar.set)
        
        self.dispo_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
    def create_kp_tab(self):
        kp_frame = ttk.Frame(self.notebook)
        self.notebook.add(kp_frame, text='Índice Kp')
        
        current_frame = ttk.Frame(kp_frame)
        current_frame.pack(fill='x', padx=10, pady=5)
        
        kp_card = self.create_card(current_frame, "Índice Kp Atual")
        self.kp_label = ttk.Label(kp_card, text="Valor: --\nEstimativa: --", style='Data.TLabel', font=('Helvetica', 24))
        self.kp_label.pack(padx=10, pady=5)
        
        data_frame = ttk.Frame(kp_frame)
        data_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        self.fig_kp = Figure(figsize=(6, 4), dpi=100)
        self.ax_kp = self.fig_kp.add_subplot(111)
        self.canvas_kp = FigureCanvasTkAgg(self.fig_kp, master=data_frame)
        self.canvas_kp.get_tk_widget().pack(side='left', fill='both', expand=True)
        
        tables_frame = ttk.Frame(data_frame)
        tables_frame.pack(side='right', fill='both', expand=True, padx=10)
        
        hist_frame = ttk.Frame(tables_frame)
        hist_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        hist_label = ttk.Label(hist_frame, text="Histórico", style='Title.TLabel')
        hist_label.pack(anchor='w')
        
        columns = ('Data', 'Kp', 'Estimativa')
        self.kp_tree = ttk.Treeview(hist_frame, columns=columns, show='headings', height=10)
        
        for col in columns:
            self.kp_tree.heading(col, text=col)
            self.kp_tree.column(col, width=100)
        
        scrollbar = ttk.Scrollbar(hist_frame, orient='vertical', command=self.kp_tree.yview)
        self.kp_tree.configure(yscrollcommand=scrollbar.set)
        
        self.kp_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        prev_frame = ttk.Frame(tables_frame)
        prev_frame.pack(fill='both', expand=True)
        
        prev_label = ttk.Label(prev_frame, text="Previsões Futuras", style='Title.TLabel')
        prev_label.pack(anchor='w')
        
        columns = ('Data', 'Kp Previsto', 'Confiança')
        self.kp_prev_tree = ttk.Treeview(prev_frame, columns=columns, show='headings', height=5)
        
        for col in columns:
            self.kp_prev_tree.heading(col, text=col)
            self.kp_prev_tree.column(col, width=100)
        
        scrollbar_prev = ttk.Scrollbar(prev_frame, orient='vertical', command=self.kp_prev_tree.yview)
        self.kp_prev_tree.configure(yscrollcommand=scrollbar_prev.set)
        
        self.kp_prev_tree.pack(side='left', fill='both', expand=True)
        scrollbar_prev.pack(side='right', fill='y')
        
    def update_data(self):
        insta_main = main()
        insta_main.main()

        try:
            conn = meusqldb('root', 'MinhaSenhaSegura', '127.0.0.1', '3306', 'Banco_geral')
            
            dados_dispo = conn.selecionar_dados('dispositivo', {'id': 1})
            if dados_dispo:
                self.dispo_tree.delete(*self.dispo_tree.get_children())
                for key, value in dados_dispo[0].items():
                    if key != 'id':
                        self.dispo_tree.insert('', 'end', values=(key.capitalize(), value))

            dados_clima = conn.selecionar_dados('clima')
            if dados_clima:
                ultimo_clima = dados_clima[-1]
                self.temp_label.config(text=f"{ultimo_clima['temperatura']}°C")
                self.vento_label.config(
                    text=f"Velocidade: {ultimo_clima['velocidade_vent']} km/h\n"
                         f"Direção: {ultimo_clima['direcao_vent']}°"
                )
                
                self.clima_tree.delete(*self.clima_tree.get_children())
                for registro in reversed(dados_clima[-10:]):  
                    data = registro['hora'].strftime("%d/%m/%Y %H:%M")
                    self.clima_tree.insert('', 'end', values=(
                        data,
                        f"{registro['temperatura']}°C",
                        f"{registro['velocidade_vent']} km/h",
                        f"{registro['direcao_vent']}°"
                    ))
                
                self.ax_temp.clear()
                datas = [r['hora'] for r in dados_clima[-24:]]  
                temps = [r['temperatura'] for r in dados_clima[-24:]]
                self.ax_temp.plot(datas, temps, 'b-')
                self.ax_temp.set_title('Temperatura nas últimas 24 horas')
                self.ax_temp.set_xlabel('Hora')
                self.ax_temp.set_ylabel('Temperatura (°C)')
                self.ax_temp.grid(True)
                self.canvas_temp.draw()
            
            kp_indices = conn.selecionar_dados('kp_indices')
            if kp_indices:
                ultimo_kp = kp_indices[-1]
                kp_value = self.convert_kp_value(ultimo_kp['kp'])
                self.kp_label.config(
                    text=f"Valor: {ultimo_kp['kp']}\n"
                         f"Estimativa: {ultimo_kp['estimated_kp']}"
                )
                
                agora = datetime.now()
                dados_historicos = []
                previsoes = []
                
                for registro in kp_indices:
                    if registro['time_tag'] <= agora:
                        dados_historicos.append(registro)
                    else:
                        previsoes.append(registro)
                
                self.kp_tree.delete(*self.kp_tree.get_children())
                for registro in reversed(dados_historicos[-50:]):  
                    data = registro['time_tag'].strftime("%d/%m/%Y %H:%M")
                    self.kp_tree.insert('', 'end', values=(
                        data,
                        registro['kp'],
                        f"{registro['estimated_kp']:.2f}"
                    ))
                
                self.kp_prev_tree.delete(*self.kp_prev_tree.get_children())
                for registro in previsoes:
                    data = registro['time_tag'].strftime("%d/%m/%Y %H:%M")
                    confianca = "Alta" if registro['estimated_kp'] > 0.8 else "Média" if registro['estimated_kp'] > 0.5 else "Baixa"
                    self.kp_prev_tree.insert('', 'end', values=(
                        data,
                        registro['kp'],
                        confianca
                    ))
                
                self.ax_kp.clear()
                
                if dados_historicos:
                    datas_hist = [r['time_tag'] for r in dados_historicos[-24:]]
                    kps_hist = [self.convert_kp_value(r['kp']) for r in dados_historicos[-24:]]
                    self.ax_kp.plot(datas_hist, kps_hist, 'b-', label='Histórico', linewidth=2)
                
                if previsoes:
                    datas_prev = [r['time_tag'] for r in previsoes]
                    kps_prev = [self.convert_kp_value(r['kp']) for r in previsoes]
                    self.ax_kp.plot(datas_prev, kps_prev, 'r--', label='Previsão', linewidth=2)
                
                self.ax_kp.set_title('Índice Kp - Histórico e Previsão', pad=20)
                self.ax_kp.set_xlabel('Data/Hora')
                self.ax_kp.set_ylabel('Índice Kp')
                self.ax_kp.grid(True, linestyle='--', alpha=0.7)
                self.ax_kp.legend(loc='upper right')
                
                plt.setp(self.ax_kp.get_xticklabels(), rotation=45, ha='right')
                
                self.fig_kp.tight_layout()
                
                self.canvas_kp.draw()
                
        except Exception as e:
            print(f"Erro ao atualizar dados: {e}")
        
        self.root.after(300000, self.update_data)

if __name__ == "__main__":
    root = tk.Tk()
    app = Interface(root)
    root.mainloop()