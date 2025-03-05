import time
import json
import os
import datetime
import threading
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import pickle
import schedule
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

class WhatsAppScheduler:
    def __init__(self, root):
        self.root = root
        self.root.title("Agendador Automático de WhatsApp")
        self.root.geometry("800x800")
        self.root.resizable(True, True)
        
        # Variáveis para armazenar os dados
        self.messages = []
        self.driver = None
        self.is_logged_in = False
        self.scheduler_thread = None
        self.stop_thread = False
        
        # Carregar mensagens salvas
        self.load_messages()
        
        # Configurar o estilo
        self.style = ttk.Style()
        self.style.configure("TButton", font=("Arial", 12))
        self.style.configure("TLabel", font=("Arial", 12))
        self.style.configure("TEntry", font=("Arial", 12))
        
        # Frame principal
        main_frame = ttk.Frame(root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Frame de entrada
        input_frame = ttk.LabelFrame(main_frame, text="Agendar Nova Mensagem", padding="10")
        input_frame.pack(fill=tk.X, pady=5)
        
        # Entrada para o número de telefone
        ttk.Label(input_frame, text="Número de Telefone (com código do país, ex: 5511999999999):").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.phone_entry = ttk.Entry(input_frame, width=30)
        self.phone_entry.grid(row=0, column=1, sticky=tk.W, pady=5)
        
        # Entrada para a mensagem
        ttk.Label(input_frame, text="Mensagem:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.message_text = scrolledtext.ScrolledText(input_frame, width=40, height=5)
        self.message_text.grid(row=1, column=1, sticky=tk.W, pady=5)
        
        # Entrada para a data
        ttk.Label(input_frame, text="Data (DD/MM/AAAA):").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.date_entry = ttk.Entry(input_frame, width=15)
        self.date_entry.grid(row=2, column=1, sticky=tk.W, pady=5)
        self.date_entry.insert(0, datetime.datetime.now().strftime("%d/%m/%Y"))
        
        # Entrada para a hora
        ttk.Label(input_frame, text="Hora (HH:MM):").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.time_entry = ttk.Entry(input_frame, width=10)
        self.time_entry.grid(row=3, column=1, sticky=tk.W, pady=5)
        
        # Botão para agendar
        schedule_button = ttk.Button(input_frame, text="Agendar Mensagem", command=self.schedule_message)
        schedule_button.grid(row=4, column=0, columnspan=2, pady=10)
        
        # Frame de controle
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=5)
        
        # Botão para iniciar/parar o agendador
        self.start_stop_button = ttk.Button(control_frame, text="Iniciar Agendador", command=self.toggle_scheduler)
        self.start_stop_button.pack(side=tk.LEFT, padx=5)
        
        # Botão para verificar status
        status_button = ttk.Button(control_frame, text="Verificar Status WhatsApp", command=self.check_whatsapp_status)
        status_button.pack(side=tk.LEFT, padx=5)
        
        # Botão para enviar teste
        test_button = ttk.Button(control_frame, text="Enviar Mensagem de Teste", command=self.send_test_message)
        test_button.pack(side=tk.LEFT, padx=5)
        
        # Frame para lista de mensagens agendadas
        messages_frame = ttk.LabelFrame(main_frame, text="Mensagens Agendadas", padding="10")
        messages_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Treeview para exibir mensagens agendadas
        columns = ("id", "phone", "message", "schedule_time", "status")
        self.tree = ttk.Treeview(messages_frame, columns=columns, show="headings")
        
        # Definir cabeçalhos
        self.tree.heading("id", text="ID")
        self.tree.heading("phone", text="Telefone")
        self.tree.heading("message", text="Mensagem")
        self.tree.heading("schedule_time", text="Agendado para")
        self.tree.heading("status", text="Status")
        
        # Definir larguras das colunas
        self.tree.column("id", width=50)
        self.tree.column("phone", width=150)
        self.tree.column("message", width=300)
        self.tree.column("schedule_time", width=150)
        self.tree.column("status", width=100)
        
        # Adicionar scrollbar
        scrollbar = ttk.Scrollbar(messages_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        
        # Posicionar treeview e scrollbar
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Frame para os botões de gerenciamento
        buttons_frame = ttk.LabelFrame(main_frame, text="Gerenciar Mensagens", padding="10")
        buttons_frame.pack(fill=tk.X, pady=5)
        
        # Criar grid para os botões (2 linhas x 3 colunas)
        delete_button = ttk.Button(buttons_frame, text="Excluir Selecionado", command=self.delete_selected, width=20)
        delete_button.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        
        edit_button = ttk.Button(buttons_frame, text="Editar Mensagem", command=self.edit_selected, width=20)
        edit_button.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        
        reschedule_button = ttk.Button(buttons_frame, text="Reagendar", command=self.reschedule_selected, width=20)
        reschedule_button.grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        
        duplicate_button = ttk.Button(buttons_frame, text="Duplicar", command=self.duplicate_selected, width=20)
        duplicate_button.grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        
        clear_button = ttk.Button(buttons_frame, text="Limpar Todos", command=self.clear_all, width=20)
        clear_button.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        
        # Frame de status
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(status_frame, text="Status do WhatsApp:").pack(side=tk.LEFT, padx=5)
        self.status_label = ttk.Label(status_frame, text="Não conectado")
        self.status_label.pack(side=tk.LEFT, padx=5)
        
        # Exibir mensagens salvas
        self.update_message_list()
        
        # Adicionar tratamento de fechamento
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
    
    def schedule_message(self):
        """Agendar uma nova mensagem."""
        # Validar entradas
        phone = self.phone_entry.get().strip()
        message = self.message_text.get("1.0", tk.END).strip()
        date_str = self.date_entry.get().strip()
        time_str = self.time_entry.get().strip()
        
        # Verificar se todos os campos estão preenchidos
        if not all([phone, message, date_str, time_str]):
            messagebox.showerror("Erro", "Por favor, preencha todos os campos.")
            return
        
        # Validar formato do telefone
        if not phone.isdigit() or len(phone) < 10:
            messagebox.showerror("Erro", "Número de telefone inválido. Use apenas números, incluindo código do país e DDD.")
            return
        
        # Validar formato da data
        try:
            day, month, year = map(int, date_str.split('/'))
            schedule_date = datetime.date(year, month, day)
        except ValueError:
            messagebox.showerror("Erro", "Formato de data inválido. Use DD/MM/AAAA.")
            return
        
        # Validar formato da hora
        try:
            hour, minute = map(int, time_str.split(':'))
            schedule_time = datetime.time(hour, minute)
        except ValueError:
            messagebox.showerror("Erro", "Formato de hora inválido. Use HH:MM.")
            return
        
        # Combinar data e hora
        schedule_datetime = datetime.datetime.combine(schedule_date, schedule_time)
        
        # Verificar se a data é no futuro
        if schedule_datetime <= datetime.datetime.now():
            messagebox.showerror("Erro", "A data e hora de agendamento devem ser no futuro.")
            return
        
        # Criar ID único baseado no timestamp
        msg_id = int(time.time())
        
        # Criar nova mensagem
        new_message = {
            "id": msg_id,
            "phone": phone,
            "message": message,
            "schedule_time": schedule_datetime.strftime("%Y-%m-%d %H:%M:%S"),
            "status": "Agendado"
        }
        
        # Adicionar à lista de mensagens
        self.messages.append(new_message)
        
        # Salvar mensagens
        self.save_messages()
        
        # Atualizar a lista na interface
        self.update_message_list()
        
        # Limpar campos
        self.phone_entry.delete(0, tk.END)
        self.message_text.delete("1.0", tk.END)
        self.time_entry.delete(0, tk.END)
        
        messagebox.showinfo("Sucesso", "Mensagem agendada com sucesso.")
    
    def update_message_list(self):
        """Atualizar a lista de mensagens na interface."""
        # Limpar lista atual
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Ordenar mensagens por data/hora
        sorted_messages = sorted(self.messages, key=lambda x: x["schedule_time"])
        
        # Adicionar mensagens à lista
        for msg in sorted_messages:
            # Formatar data/hora para exibição
            schedule_time = datetime.datetime.strptime(msg["schedule_time"], "%Y-%m-%d %H:%M:%S")
            formatted_time = schedule_time.strftime("%d/%m/%Y %H:%M")
            
            # Truncar mensagem longa para exibição
            display_message = msg["message"]
            if len(display_message) > 40:
                display_message = display_message[:37] + "..."
            
            self.tree.insert("", tk.END, values=(
                msg["id"],
                msg["phone"],
                display_message,
                formatted_time,
                msg["status"]
            ))
    
    def delete_selected(self):
        """Excluir a mensagem selecionada."""
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("Aviso", "Selecione uma mensagem para excluir.")
            return
        
        if len(selected_items) > 1:
            confirm = messagebox.askyesno("Confirmar", f"Deseja excluir {len(selected_items)} mensagens selecionadas?")
        else:
            confirm = messagebox.askyesno("Confirmar", "Deseja excluir a mensagem selecionada?")
            
        if not confirm:
            return
            
        # Processar todas as mensagens selecionadas
        for item in selected_items:
            # Obter ID da mensagem selecionada
            msg_id = int(self.tree.item(item)["values"][0])
            
            # Remover da lista
            self.messages = [msg for msg in self.messages if msg["id"] != msg_id]
        
        # Salvar e atualizar
        self.save_messages()
        self.update_message_list()
        messagebox.showinfo("Sucesso", f"{len(selected_items)} mensagem(ns) excluída(s) com sucesso.")
    
    def clear_all(self):
        """Limpar todas as mensagens."""
        if not self.messages:
            messagebox.showinfo("Info", "Não há mensagens para limpar.")
            return
        
        # Opções avançadas para limpeza
        clear_options = ["Todas as mensagens", 
                         "Apenas mensagens já enviadas", 
                         "Apenas mensagens com erro",
                         "Mensagens mais antigas que uma semana",
                         "Cancelar"]
        
        from tkinter import simpledialog
        
        choice = simpledialog.askstring(
            "Opções de Limpeza",
            "Escolha o que deseja limpar:\n\n"
            "1. Todas as mensagens\n"
            "2. Apenas mensagens já enviadas\n"
            "3. Apenas mensagens com erro\n"
            "4. Mensagens mais antigas que uma semana\n"
            "5. Cancelar",
            initialvalue="1"
        )
        
        if not choice or choice == "5":
            return
        
        try:
            choice = int(choice)
            if choice < 1 or choice > 5:
                raise ValueError
        except ValueError:
            messagebox.showerror("Erro", "Opção inválida.")
            return
        
        # Processamento baseado na escolha
        if choice == 1:  # Todas as mensagens
            if messagebox.askyesno("Confirmar", "Tem certeza que deseja excluir TODAS as mensagens?"):
                self.messages = []
                messagebox.showinfo("Sucesso", "Todas as mensagens foram excluídas.")
        
        elif choice == 2:  # Apenas enviadas
            old_count = len(self.messages)
            self.messages = [msg for msg in self.messages if msg["status"] != "Enviado"]
            deleted = old_count - len(self.messages)
            messagebox.showinfo("Sucesso", f"{deleted} mensagem(ns) enviada(s) foi(ram) excluída(s).")
        
        elif choice == 3:  # Apenas com erro
            old_count = len(self.messages)
            self.messages = [msg for msg in self.messages if msg["status"] != "Falha"]
            deleted = old_count - len(self.messages)
            messagebox.showinfo("Sucesso", f"{deleted} mensagem(ns) com erro foi(ram) excluída(s).")
        
        elif choice == 4:  # Mais antigas que uma semana
            old_count = len(self.messages)
            one_week_ago = datetime.datetime.now() - datetime.timedelta(days=7)
            self.messages = [msg for msg in self.messages if 
                           datetime.datetime.strptime(msg["schedule_time"], "%Y-%m-%d %H:%M:%S") > one_week_ago]
            deleted = old_count - len(self.messages)
            messagebox.showinfo("Sucesso", f"{deleted} mensagem(ns) antiga(s) foi(ram) excluída(s).")
        
        # Salvar e atualizar
        self.save_messages()
        self.update_message_list()
    
    def save_messages(self):
        """Salvar mensagens em arquivo."""
        try:
            with open("whatsapp_messages.pickle", "wb") as f:
                pickle.dump(self.messages, f)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar mensagens: {str(e)}")
    
    def load_messages(self):
        """Carregar mensagens do arquivo."""
        try:
            if os.path.exists("whatsapp_messages.pickle"):
                with open("whatsapp_messages.pickle", "rb") as f:
                    self.messages = pickle.load(f)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar mensagens: {str(e)}")
            self.messages = []
    
    def init_whatsapp_driver(self):
        """Inicializar o driver do Selenium para o WhatsApp Web."""
        try:
            # Configurar opções do Chrome
            chrome_options = Options()
            chrome_options.add_argument("--start-maximized")
            chrome_options.add_argument("--disable-notifications")
            chrome_options.add_argument("--disable-infobars")
            
            # Inicializar o driver
            self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
            
            # Abrir o WhatsApp Web
            self.driver.get("https://web.whatsapp.com/")
            
            # Aguardar carregamento da página e verificar login
            try:
                # Esperar pelo elemento que indica que o WhatsApp Web está pronto
                WebDriverWait(self.driver, 30).until(
                    EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"][@data-tab="3"]'))
                )
                self.is_logged_in = True
                self.status_label.config(text="Conectado")
                return True
            except TimeoutException:
                messagebox.showwarning("Aviso", "Tempo excedido. Escaneie o código QR para fazer login no WhatsApp Web.")
                # Dar mais tempo para o usuário escanear o QR code
                try:
                    WebDriverWait(self.driver, 60).until(
                        EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"][@data-tab="3"]'))
                    )
                    self.is_logged_in = True
                    self.status_label.config(text="Conectado")
                    return True
                except TimeoutException:
                    messagebox.showerror("Erro", "Falha ao fazer login no WhatsApp Web. Tente novamente.")
                    self.driver.quit()
                    self.driver = None
                    self.is_logged_in = False
                    self.status_label.config(text="Não conectado")
                    return False
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao inicializar o WhatsApp: {str(e)}")
            self.driver = None
            self.is_logged_in = False
            self.status_label.config(text="Erro")
            return False
    
    def send_whatsapp_message(self, phone, message):
        """Enviar mensagem para o WhatsApp."""
        if not self.driver or not self.is_logged_in:
            if not self.init_whatsapp_driver():
                return False
        
        try:
            # Formatar URL direta para o contato
            self.driver.get(f"https://web.whatsapp.com/send?phone={phone}&text={message}")
            
            # Esperar que a página carregue e a caixa de texto esteja disponível
            message_box = WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"][@data-tab="10"]'))
            )
            
            # Enviar a mensagem pressionando Enter
            message_box.send_keys("\n")
            
            # Aguardar um momento para garantir que a mensagem seja enviada
            time.sleep(3)
            
            return True
        except TimeoutException:
            messagebox.showerror("Erro", "Tempo excedido ao tentar enviar a mensagem.")
            return False
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao enviar mensagem: {str(e)}")
            return False
    
    def check_whatsapp_status(self):
        """Verificar o status da conexão com o WhatsApp."""
        if not self.driver:
            if self.init_whatsapp_driver():
                messagebox.showinfo("Status", "Conectado ao WhatsApp Web.")
            else:
                messagebox.showwarning("Status", "Não conectado ao WhatsApp Web.")
        else:
            try:
                # Verificar se ainda está na página do WhatsApp
                if "whatsapp" in self.driver.current_url:
                    try:
                        # Verificar se há elemento que confirma login
                        self.driver.find_element(By.XPATH, '//div[@contenteditable="true"][@data-tab="3"]')
                        messagebox.showinfo("Status", "Conectado ao WhatsApp Web.")
                        self.is_logged_in = True
                        self.status_label.config(text="Conectado")
                    except NoSuchElementException:
                        messagebox.showwarning("Status", "Sessão do WhatsApp Web expirada. Faça login novamente.")
                        self.is_logged_in = False
                        self.status_label.config(text="Desconectado")
                        self.init_whatsapp_driver()
                else:
                    messagebox.showwarning("Status", "Navegador não está na página do WhatsApp. Reconectando...")
                    self.driver.get("https://web.whatsapp.com/")
                    self.init_whatsapp_driver()
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao verificar status: {str(e)}")
                self.is_logged_in = False
                self.status_label.config(text="Erro")
    
    def send_test_message(self):
        """Enviar uma mensagem de teste."""
        phone = self.phone_entry.get().strip()
        message = self.message_text.get("1.0", tk.END).strip()
        
        if not phone or not message:
            messagebox.showerror("Erro", "Preencha o número de telefone e a mensagem para teste.")
            return
        
        if not phone.isdigit() or len(phone) < 10:
            messagebox.showerror("Erro", "Número de telefone inválido. Use apenas números, incluindo código do país e DDD.")
            return
        
        result = self.send_whatsapp_message(phone, message)
        if result:
            messagebox.showinfo("Sucesso", "Mensagem de teste enviada com sucesso.")
        else:
            messagebox.showerror("Erro", "Falha ao enviar mensagem de teste.")
    
    def toggle_scheduler(self):
        """Iniciar ou parar o agendador."""
        if self.scheduler_thread and self.scheduler_thread.is_alive():
            # Parar o agendador
            self.stop_thread = True
            self.start_stop_button.config(text="Iniciar Agendador")
            messagebox.showinfo("Info", "Agendador parado.")
        else:
            # Iniciar o agendador
            if not self.messages:
                messagebox.showwarning("Aviso", "Não há mensagens agendadas.")
                return
            
            # Verificar conexão com WhatsApp
            if not self.driver or not self.is_logged_in:
                if not self.init_whatsapp_driver():
                    messagebox.showerror("Erro", "Não foi possível conectar ao WhatsApp Web. O agendador não pode ser iniciado.")
                    return
            
            self.stop_thread = False
            self.scheduler_thread = threading.Thread(target=self.run_scheduler)
            self.scheduler_thread.daemon = True
            self.scheduler_thread.start()
            
            self.start_stop_button.config(text="Parar Agendador")
            messagebox.showinfo("Info", "Agendador iniciado.")
    
    def run_scheduler(self):
        """Função principal do agendador."""
        # Limpar agendamentos anteriores
        schedule.clear()
        
        # Agendar verificação periódica
        while not self.stop_thread:
            # Verificar mensagens a serem enviadas
            current_time = datetime.datetime.now()
            
            for msg in self.messages[:]:  # Usar uma cópia para evitar problemas ao modificar durante iteração
                if msg["status"] == "Agendado" or msg["status"] == "Reagendado":
                    schedule_time = datetime.datetime.strptime(msg["schedule_time"], "%Y-%m-%d %H:%M:%S")
                    
                    # Se chegou a hora de enviar
                    if current_time >= schedule_time:
                        # Atualizar status
                        msg["status"] = "Enviando..."
                        self.update_message_list()
                        
                        # Enviar mensagem
                        success = self.send_whatsapp_message(msg["phone"], msg["message"])
                        
                        if success:
                            msg["status"] = "Enviado"
                        else:
                            msg["status"] = "Falha"
                        
                        # Atualizar interface e salvar
                        self.root.after(0, self.update_message_list)
                        self.save_messages()
            
            # Verificar a cada 10 segundos
            time.sleep(10)
            
            # Se o sinalizador de parada estiver ativo, sair do loop
            if self.stop_thread:
                break
    
    def edit_selected(self):
        """Editar a mensagem selecionada."""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Aviso", "Selecione uma mensagem para editar.")
            return
        
        # Obter ID da mensagem selecionada
        msg_id = int(self.tree.item(selected_item[0])["values"][0])
        
        # Encontrar a mensagem na lista
        selected_msg = None
        for msg in self.messages:
            if msg["id"] == msg_id:
                selected_msg = msg
                break
        
        if not selected_msg:
            messagebox.showerror("Erro", "Mensagem não encontrada.")
            return
        
        # Verificar se a mensagem já foi enviada
        if selected_msg["status"] == "Enviado":
            messagebox.showwarning("Aviso", "Não é possível editar uma mensagem já enviada.")
            return
        
        # Criar uma janela de diálogo para edição
        edit_window = tk.Toplevel(self.root)
        edit_window.title("Editar Mensagem")
        edit_window.geometry("500x400")
        edit_window.resizable(False, False)
        edit_window.transient(self.root)
        edit_window.grab_set()
        
        # Frame principal
        edit_frame = ttk.Frame(edit_window, padding="10")
        edit_frame.pack(fill=tk.BOTH, expand=True)
        
        # Campos de edição
        ttk.Label(edit_frame, text="Número de Telefone:").grid(row=0, column=0, sticky=tk.W, pady=5)
        phone_entry = ttk.Entry(edit_frame, width=30)
        phone_entry.grid(row=0, column=1, sticky=tk.W, pady=5)
        phone_entry.insert(0, selected_msg["phone"])
        
        ttk.Label(edit_frame, text="Mensagem:").grid(row=1, column=0, sticky=tk.W, pady=5)
        message_text = scrolledtext.ScrolledText(edit_frame, width=40, height=10)
        message_text.grid(row=1, column=1, sticky=tk.W, pady=5)
        message_text.insert("1.0", selected_msg["message"])
        
        # Botões
        buttons_frame = ttk.Frame(edit_frame)
        buttons_frame.grid(row=2, column=0, columnspan=2, pady=10)
        
        save_button = ttk.Button(buttons_frame, text="Salvar", width=10, command=lambda: self.save_edited_message(
            edit_window, msg_id, phone_entry.get(), message_text.get("1.0", tk.END).strip()))
        save_button.pack(side=tk.LEFT, padx=5)
        
        cancel_button = ttk.Button(buttons_frame, text="Cancelar", width=10, command=edit_window.destroy)
        cancel_button.pack(side=tk.LEFT, padx=5)
    
    def save_edited_message(self, window, msg_id, phone, message):
        """Salvar a mensagem editada."""
        # Validar número de telefone
        if not phone.isdigit() or len(phone) < 10:
            messagebox.showerror("Erro", "Número de telefone inválido. Use apenas números, incluindo código do país e DDD.")
            return
        
        # Validar mensagem
        if not message:
            messagebox.showerror("Erro", "A mensagem não pode estar vazia.")
            return
        
        # Atualizar a mensagem
        for msg in self.messages:
            if msg["id"] == msg_id:
                msg["phone"] = phone
                msg["message"] = message
                break
        
        # Salvar e atualizar
        self.save_messages()
        self.update_message_list()
        
        # Fechar janela de edição
        window.destroy()
        
        messagebox.showinfo("Sucesso", "Mensagem atualizada com sucesso.")
    
    def reschedule_selected(self):
        """Reagendar a mensagem selecionada."""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Aviso", "Selecione uma mensagem para reagendar.")
            return
        
        # Obter ID da mensagem selecionada
        msg_id = int(self.tree.item(selected_item[0])["values"][0])
        
        # Encontrar a mensagem na lista
        selected_msg = None
        for msg in self.messages:
            if msg["id"] == msg_id:
                selected_msg = msg
                break
        
        if not selected_msg:
            messagebox.showerror("Erro", "Mensagem não encontrada.")
            return
        
        # Verificar se a mensagem já foi enviada
        if selected_msg["status"] == "Enviado":
            messagebox.showwarning("Aviso", "Não é possível reagendar uma mensagem já enviada.")
            return
        
        # Obter a data e hora atual
        current_datetime = datetime.datetime.strptime(selected_msg["schedule_time"], "%Y-%m-%d %H:%M:%S")
        current_date = current_datetime.strftime("%d/%m/%Y")
        current_time = current_datetime.strftime("%H:%M")
        
        # Criar uma janela de diálogo para edição
        reschedule_window = tk.Toplevel(self.root)
        reschedule_window.title("Reagendar Mensagem")
        reschedule_window.geometry("400x200")
        reschedule_window.resizable(False, False)
        reschedule_window.transient(self.root)
        reschedule_window.grab_set()
        
        # Frame principal
        reschedule_frame = ttk.Frame(reschedule_window, padding="10")
        reschedule_frame.pack(fill=tk.BOTH, expand=True)
        
        # Campos de edição
        ttk.Label(reschedule_frame, text="Nova Data (DD/MM/AAAA):").grid(row=0, column=0, sticky=tk.W, pady=5)
        date_entry = ttk.Entry(reschedule_frame, width=15)
        date_entry.grid(row=0, column=1, sticky=tk.W, pady=5)
        date_entry.insert(0, current_date)
        
        ttk.Label(reschedule_frame, text="Nova Hora (HH:MM):").grid(row=1, column=0, sticky=tk.W, pady=5)
        time_entry = ttk.Entry(reschedule_frame, width=10)
        time_entry.grid(row=1, column=1, sticky=tk.W, pady=5)
        time_entry.insert(0, current_time)
        
        # Botões
        buttons_frame = ttk.Frame(reschedule_frame)
        buttons_frame.grid(row=2, column=0, columnspan=2, pady=10)
        
        save_button = ttk.Button(buttons_frame, text="Salvar", width=10, command=lambda: self.save_rescheduled_message(
            reschedule_window, msg_id, date_entry.get(), time_entry.get()))
        save_button.pack(side=tk.LEFT, padx=5)
        
        cancel_button = ttk.Button(buttons_frame, text="Cancelar", width=10, command=reschedule_window.destroy)
        cancel_button.pack(side=tk.LEFT, padx=5)
    
    def save_rescheduled_message(self, window, msg_id, date_str, time_str):
        """Salvar a nova data/hora da mensagem."""
        # Validar formato da data
        try:
            day, month, year = map(int, date_str.split('/'))
            schedule_date = datetime.date(year, month, day)
        except ValueError:
            messagebox.showerror("Erro", "Formato de data inválido. Use DD/MM/AAAA.")
            return
        
        # Validar formato da hora
        try:
            hour, minute = map(int, time_str.split(':'))
            schedule_time = datetime.time(hour, minute)
        except ValueError:
            messagebox.showerror("Erro", "Formato de hora inválido. Use HH:MM.")
            return
        
        # Combinar data e hora
        schedule_datetime = datetime.datetime.combine(schedule_date, schedule_time)
        
        # Verificar se a data é no futuro
        if schedule_datetime <= datetime.datetime.now():
            messagebox.showerror("Erro", "A data e hora de agendamento devem ser no futuro.")
            return
        
        # Atualizar a mensagem
        for msg in self.messages:
            if msg["id"] == msg_id:
                msg["schedule_time"] = schedule_datetime.strftime("%Y-%m-%d %H:%M:%S")
                msg["status"] = "Reagendado"  # Atualizar status
                break
        
        # Salvar e atualizar
        self.save_messages()
        self.update_message_list()
        
        # Fechar janela de edição
        window.destroy()
        
        messagebox.showinfo("Sucesso", "Mensagem reagendada com sucesso.")
    
    def duplicate_selected(self):
        """Duplica a mensagem selecionada."""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Aviso", "Selecione uma mensagem para duplicar.")
            return
        
        # Obter ID da mensagem selecionada
        msg_id = int(self.tree.item(selected_item[0])["values"][0])
        
        # Encontrar a mensagem na lista
        selected_msg = None
        for msg in self.messages:
            if msg["id"] == msg_id:
                selected_msg = msg
                break
        
        if not selected_msg:
            messagebox.showerror("Erro", "Mensagem não encontrada.")
            return
        
        # Criar uma cópia da mensagem com um novo ID
        new_id = int(time.time())
        new_msg = selected_msg.copy()
        new_msg["id"] = new_id
        new_msg["status"] = "Agendado"
        
        # Adicionar à lista
        self.messages.append(new_msg)
        
        # Salvar e atualizar
        self.save_messages()
        self.update_message_list()
        
        messagebox.showinfo("Sucesso", "Mensagem duplicada com sucesso.")
        
    def on_close(self):
        """Manipular fechamento da aplicação."""
        if self.scheduler_thread and self.scheduler_thread.is_alive():
            if not messagebox.askyesno("Confirmar", "O agendador está em execução. Deseja realmente sair?"):
                return
            self.stop_thread = True
        
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
        
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = WhatsAppScheduler(root)
    root.mainloop()