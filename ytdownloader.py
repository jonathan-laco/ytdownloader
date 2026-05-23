import os
import sys
import threading
import subprocess
import customtkinter as ctk
from tkinter import filedialog
import yt_dlp
import imageio_ffmpeg

# Configura o visual moderno do CustomTkinter
ctk.set_appearance_mode("Dark")  # Opções: "System", "Dark", "Light"
ctk.set_default_color_theme("blue")  # Temas padrão: "blue", "green", "dark-blue"

class YTDownloaderApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Configuração da janela
        self.title("YouTube Downloader Pro")
        self.geometry("780x720")
        self.resizable(True, True)
        
        # Variáveis de controle
        self.stop_flag = False
        self.download_thread = None
        
        # Pasta de downloads padrão do usuário (Downloads no Windows)
        self.default_dir = os.path.join(os.path.expanduser("~"), "Downloads")
        if not os.path.exists(self.default_dir):
            self.default_dir = os.getcwd()
            
        # Construção da interface
        self.create_widgets()
        
    def create_widgets(self):
        # Grid layout principal
        self.grid_rowconfigure((0, 1, 2, 3, 4, 5, 6, 7), weight=0)
        self.grid_rowconfigure(8, weight=1) # A caixa de logs expande verticalmente
        self.grid_columnconfigure(0, weight=1)
        
        # --- 1. CABEÇALHO (Header) ---
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        
        title_label = ctk.CTkLabel(
            header_frame, 
            text="YouTube Downloader Pro", 
            font=ctk.CTkFont(family="Helvetica", size=26, weight="bold"),
            text_color="#FF2A54" # Vermelho vibrante estilo YouTube premium
        )
        title_label.pack(anchor="w")
        
        subtitle_label = ctk.CTkLabel(
            header_frame, 
            text="Baixe vídeos e playlists com máxima performance e converta para áudio em alta definição.", 
            font=ctk.CTkFont(family="Helvetica", size=13),
            text_color="gray"
        )
        subtitle_label.pack(anchor="w", pady=(2, 0))
        
        # Linha separadora estética
        sep = ctk.CTkFrame(self, height=2, fg_color="#2A2A3E")
        sep.grid(row=1, column=0, padx=20, pady=5, sticky="ew")
        
        # --- 2. SELEÇÃO DA PASTA DE DESTINO ---
        folder_frame = ctk.CTkFrame(self, fg_color="transparent")
        folder_frame.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        folder_frame.grid_columnconfigure(0, weight=1)
        
        folder_label = ctk.CTkLabel(
            folder_frame, 
            text="Pasta de Salvamento:", 
            font=ctk.CTkFont(weight="bold")
        )
        folder_label.grid(row=0, column=0, sticky="w", pady=(0, 5))
        
        self.folder_entry = ctk.CTkEntry(
            folder_frame, 
            placeholder_text="Selecione o diretório onde deseja salvar...",
            height=35
        )
        self.folder_entry.grid(row=1, column=0, sticky="ew", padx=(0, 10))
        self.folder_entry.insert(0, self.default_dir)
        
        browse_btn = ctk.CTkButton(
            folder_frame, 
            text="Escolher Pasta", 
            width=130,
            height=35,
            fg_color="#2E2E3E",
            hover_color="#3E3E56",
            command=self.browse_folder
        )
        browse_btn.grid(row=1, column=1, sticky="e")
        
        # --- 3. URL DO VÍDEO OU PLAYLIST ---
        url_frame = ctk.CTkFrame(self, fg_color="transparent")
        url_frame.grid(row=3, column=0, padx=20, pady=10, sticky="ew")
        url_frame.grid_columnconfigure(0, weight=1)
        
        url_label = ctk.CTkLabel(
            url_frame, 
            text="Link do Vídeo ou Playlist do YouTube:", 
            font=ctk.CTkFont(weight="bold")
        )
        url_label.grid(row=0, column=0, sticky="w", pady=(0, 5))
        
        self.url_entry = ctk.CTkEntry(
            url_frame, 
            placeholder_text="Ex: https://www.youtube.com/watch?v=... ou link de playlist",
            height=35
        )
        self.url_entry.grid(row=1, column=0, sticky="ew")
        
        # --- 4. OPÇÕES DE DOWNLOAD (Tipo e Qualidade) ---
        settings_frame = ctk.CTkFrame(self, fg_color="#1E1E2E", corner_radius=8, border_width=1, border_color="#2E2E3E")
        settings_frame.grid(row=4, column=0, padx=20, pady=10, sticky="ew")
        settings_frame.grid_columnconfigure((0, 1), weight=1)
        
        # Subframe Tipo
        type_subframe = ctk.CTkFrame(settings_frame, fg_color="transparent")
        type_subframe.grid(row=0, column=0, padx=15, pady=15, sticky="nsew")
        
        type_label = ctk.CTkLabel(
            type_subframe, 
            text="Tipo de Formato:", 
            font=ctk.CTkFont(weight="bold")
        )
        type_label.pack(anchor="w", pady=(0, 5))
        
        self.type_segmented = ctk.CTkSegmentedButton(
            type_subframe,
            values=["Vídeo (MP4)", "Áudio (MP3)"],
            command=self.toggle_quality_menu,
            height=35
        )
        self.type_segmented.pack(fill="x")
        self.type_segmented.set("Vídeo (MP4)")
        
        # Subframe Qualidade
        quality_subframe = ctk.CTkFrame(settings_frame, fg_color="transparent")
        quality_subframe.grid(row=0, column=1, padx=15, pady=15, sticky="nsew")
        
        quality_label = ctk.CTkLabel(
            quality_subframe, 
            text="Qualidade Máxima de Vídeo:", 
            font=ctk.CTkFont(weight="bold")
        )
        quality_label.pack(anchor="w", pady=(0, 5))
        
        self.quality_option = ctk.CTkOptionMenu(
            quality_subframe,
            values=["Melhor Disponível", "1080p (Full HD)", "720p (HD)", "480p (SD)"],
            height=35
        )
        self.quality_option.pack(fill="x")
        
        # --- 5. PAINEL DE PROGRESSO ---
        self.progress_frame = ctk.CTkFrame(self, fg_color="#181824", border_width=1, border_color="#2E2E3E", corner_radius=8)
        self.progress_frame.grid(row=5, column=0, padx=20, pady=10, sticky="ew")
        self.progress_frame.grid_columnconfigure((0, 1), weight=1)
        
        self.status_label = ctk.CTkLabel(
            self.progress_frame, 
            text="Status: Aguardando download...", 
            font=ctk.CTkFont(slant="italic"),
            text_color="gray"
        )
        self.status_label.grid(row=0, column=0, columnspan=2, padx=15, pady=(10, 5), sticky="w")
        
        self.progress_bar = ctk.CTkProgressBar(self.progress_frame, height=12, progress_color="#FF2A54")
        self.progress_bar.grid(row=1, column=0, columnspan=2, padx=15, pady=5, sticky="ew")
        self.progress_bar.set(0)
        
        # Estatísticas adicionais
        self.percent_label = ctk.CTkLabel(self.progress_frame, text="Progresso: 0.0%", font=ctk.CTkFont(size=12, weight="bold"))
        self.percent_label.grid(row=2, column=0, padx=15, pady=(5, 10), sticky="w")
        
        stats_subframe = ctk.CTkFrame(self.progress_frame, fg_color="transparent")
        stats_subframe.grid(row=2, column=1, padx=15, pady=(5, 10), sticky="e")
        
        self.speed_label = ctk.CTkLabel(stats_subframe, text="Velocidade: --", font=ctk.CTkFont(size=12), text_color="gray")
        self.speed_label.pack(side="left", padx=10)
        
        self.eta_label = ctk.CTkLabel(stats_subframe, text="Restante: --", font=ctk.CTkFont(size=12), text_color="gray")
        self.eta_label.pack(side="left", padx=10)
        
        self.size_label = ctk.CTkLabel(stats_subframe, text="Tamanho: --", font=ctk.CTkFont(size=12), text_color="gray")
        self.size_label.pack(side="left", padx=10)
        
        # --- 6. BOTÕES DE AÇÃO ---
        actions_frame = ctk.CTkFrame(self, fg_color="transparent")
        actions_frame.grid(row=6, column=0, padx=20, pady=10, sticky="ew")
        actions_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        self.start_btn = ctk.CTkButton(
            actions_frame, 
            text="INICIAR DOWNLOAD", 
            fg_color="#FF2A54",
            hover_color="#D61A3F",
            height=42,
            font=ctk.CTkFont(weight="bold"),
            command=self.start_download
        )
        self.start_btn.grid(row=0, column=0, padx=(0, 5), sticky="ew")
        
        self.stop_btn = ctk.CTkButton(
            actions_frame, 
            text="CANCELAR", 
            fg_color="#3E3E56",
            hover_color="#4F4F6E",
            height=42,
            font=ctk.CTkFont(weight="bold"),
            state="disabled",
            command=self.stop_download
        )
        self.stop_btn.grid(row=0, column=1, padx=5, sticky="ew")
        
        self.convert_btn = ctk.CTkButton(
            actions_frame, 
            text="CONVERTER MP4 -> MP3", 
            fg_color="#2E2E3E",
            hover_color="#3E3E56",
            height=42,
            font=ctk.CTkFont(weight="bold"),
            command=self.start_local_conversion
        )
        self.convert_btn.grid(row=0, column=2, padx=(5, 0), sticky="ew")
        
        # --- 7. TÍTULO DOS LOGS E BOTÃO DE LIMPEZA ---
        log_frame = ctk.CTkFrame(self, fg_color="transparent")
        log_frame.grid(row=7, column=0, padx=20, pady=(15, 5), sticky="ew")
        
        log_title = ctk.CTkLabel(
            log_frame, 
            text="Histórico e Registro de Ações (Logs):", 
            font=ctk.CTkFont(weight="bold")
        )
        log_title.pack(side="left")
        
        clear_log_btn = ctk.CTkButton(
            log_frame,
            text="Limpar logs",
            width=80,
            height=20,
            fg_color="transparent",
            text_color="gray",
            hover_color="#2E2E3E",
            command=self.clear_logs
        )
        clear_log_btn.pack(side="right")
        
        # --- 8. ÁREA DE TEXTO DOS LOGS ---
        self.log_textbox = ctk.CTkTextbox(
            self,
            font=ctk.CTkFont(family="Consolas", size=11),
            fg_color="#0F0F16",
            border_width=1,
            border_color="#1E1E2E",
            corner_radius=8
        )
        self.log_textbox.grid(row=8, column=0, padx=20, pady=(0, 20), sticky="nsew")
        self.log_textbox.configure(state="disabled")
        
        # Logs Iniciais de Inicialização
        self.log(">>> SISTEMA PRONTO <<<")
        self.log("Você pode colar links de vídeos individuais ou playlists completas do YouTube.")
        self.log(f"FFmpeg integrado automaticamente usando: {imageio_ffmpeg.get_ffmpeg_exe()}")
        
    def log(self, message):
        """Escreve uma mensagem de log na caixa de texto de forma segura para threads."""
        def run_in_main_thread():
            self.log_textbox.configure(state="normal")
            self.log_textbox.insert("end", message + "\n")
            self.log_textbox.see("end")
            self.log_textbox.configure(state="disabled")
        self.after(0, run_in_main_thread)
        
    def clear_logs(self):
        self.log_textbox.configure(state="normal")
        self.log_textbox.delete("1.0", "end")
        self.log_textbox.configure(state="disabled")
        self.log("Histórico de logs limpo.")
        
    def browse_folder(self):
        """Abre o seletor de diretório nativo."""
        folder = filedialog.askdirectory(initialdir=self.folder_entry.get())
        if folder:
            self.folder_entry.delete(0, "end")
            self.folder_entry.insert(0, folder)
            self.log(f"Destino alterado para: {folder}")
            
    def toggle_quality_menu(self, selection):
        """Desativa a seleção de qualidade de vídeo quando o formato escolhido é áudio."""
        if selection == "Áudio (MP3)":
            self.quality_option.configure(state="disabled")
        else:
            self.quality_option.configure(state="normal")
            
    def update_progress_ui(self, percent, speed_str, eta_str, size_str, filename, playlist_index=None, playlist_count=None):
        """Atualiza os elementos gráficos da barra de progresso de forma thread-safe."""
        def run_in_main():
            self.progress_bar.set(percent)
            self.percent_label.configure(text=f"Progresso: {percent*100:.1f}%")
            self.speed_label.configure(text=f"Velocidade: {speed_str}")
            self.eta_label.configure(text=f"Restante: {eta_str}")
            self.size_label.configure(text=f"Tamanho: {size_str}")
            
            if playlist_index and playlist_count:
                status = f"Baixando ({playlist_index}/{playlist_count}): {filename}"
            else:
                status = f"Baixando: {filename}"
            self.status_label.configure(text=status, text_color="white")
        self.after(0, run_in_main)
        
    def start_download(self):
        """Inicia o fluxo de download em background."""
        url = self.url_entry.get().strip()
        folder = self.folder_entry.get().strip()
        
        if not url:
            self.log("[Erro] Por favor, insira o link do YouTube.")
            return
        if not folder:
            self.log("[Erro] Por favor, defina uma pasta de destino.")
            return
            
        if not os.path.exists(folder):
            try:
                os.makedirs(folder, exist_ok=True)
                self.log(f"Criando pasta de salvamento: {folder}")
            except Exception as e:
                self.log(f"[Erro] Falha ao criar pasta: {str(e)}")
                return
                
        self.stop_flag = False
        download_type = self.type_segmented.get()
        quality = self.quality_option.get()
        
        # Atualiza o estado dos botões para evitar ações paralelas
        self.start_btn.configure(state="disabled")
        self.convert_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal", fg_color="#D9534F", hover_color="#C9302C")
        
        self.status_label.configure(text="Status: Conectando ao YouTube...", text_color="yellow")
        
        # Cria e inicia a Thread de download
        self.download_thread = threading.Thread(
            target=self.download_worker, 
            args=(url, folder, download_type, quality), 
            daemon=True
        )
        self.download_thread.start()
        
    def stop_download(self):
        """Solicita o cancelamento e interrompe o loop."""
        self.stop_flag = True
        self.log("Cancelamento solicitado. Interrompendo downloads...")
        self.stop_btn.configure(state="disabled")
        
    def download_worker(self, url, folder, download_type, quality):
        """Executa a lógica de download em background utilizando yt-dlp."""
        self.log("-" * 60)
        self.log(f"Iniciando Download...")
        self.log(f"Link: {url}")
        self.log(f"Formato: {download_type}")
        if download_type == "Vídeo (MP4)":
            self.log(f"Qualidade Solicitada: {quality}")
            
        # Hook para monitorar o progresso
        def progress_hook(d):
            if self.stop_flag:
                raise Exception("Cancelado pelo usuário")
                
            if d['status'] == 'downloading':
                downloaded = d.get('downloaded_bytes', 0)
                total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
                speed = d.get('speed')
                eta = d.get('eta')
                
                percent = downloaded / total if total and total > 0 else 0
                
                # Conversão de velocidade
                if speed:
                    if speed > 1024 * 1024:
                        speed_str = f"{speed / (1024*1024):.2f} MB/s"
                    else:
                        speed_str = f"{speed / 1024:.2f} KB/s"
                else:
                    speed_str = "-- KB/s"
                    
                # Conversão de tempo restante (ETA)
                eta_str = f"{eta}s" if eta else "--s"
                
                # Conversão de tamanho
                if total:
                    total_mb = total / (1024*1024)
                    downloaded_mb = downloaded / (1024*1024)
                    size_str = f"{downloaded_mb:.1f} MB / {total_mb:.1f} MB"
                else:
                    downloaded_mb = downloaded / (1024*1024)
                    size_str = f"{downloaded_mb:.1f} MB"
                    
                filename = os.path.basename(d.get('filename', ''))
                
                info = d.get('info_dict', {})
                playlist_index = info.get('playlist_index')
                playlist_count = info.get('playlist_count') or info.get('n_entries')
                
                self.update_progress_ui(percent, speed_str, eta_str, size_str, filename, playlist_index, playlist_count)
                
            elif d['status'] == 'finished':
                self.update_progress_ui(1.0, "0.0 B/s", "0s", "Concluído", "Finalizando processamento do arquivo...", None, None)
                
        # Logger personalizado para enviar mensagens para o console da janela
        class YtdlLogger:
            def __init__(self, app):
                self.app = app
            def debug(self, msg):
                # Ignora linhas redundantes do progresso padrão no terminal do yt-dlp
                if not any(x in msg for x in ["[download] ", "[download]  ", "%"]):
                    self.app.log(f"[INFO] {msg}")
            def info(self, msg):
                self.app.log(msg)
            def warning(self, msg):
                self.app.log(f"[AVISO] {msg}")
            def error(self, msg):
                self.app.log(f"[ERRO] {msg}")
                
        ydl_opts = {
            'ffmpeg_location': imageio_ffmpeg.get_ffmpeg_exe(),
            'progress_hooks': [progress_hook],
            'logger': YtdlLogger(self),
            'nocheckcertificate': True,
            'ignoreerrors': True,
            'writethumbnail': False,
        }
        
        # Configurações específicas para Áudio (MP3)
        if download_type == "Áudio (MP3)":
            ydl_opts.update({
                'format': 'bestaudio/best',
                'outtmpl': os.path.join(folder, '%(title)s.%(ext)s'),
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '320', # Qualidade profissional de 320kbps
                }],
            })
        else:
            # Configurações específicas para Vídeo (MP4)
            if quality == "1080p (Full HD)":
                fmt = 'bestvideo[height<=1080]+bestaudio/best'
            elif quality == "720p (HD)":
                fmt = 'bestvideo[height<=720]+bestaudio/best'
            elif quality == "480p (SD)":
                fmt = 'bestvideo[height<=480]+bestaudio/best'
            else: # Melhor Disponível (suporta 4K/2K)
                fmt = 'bestvideo+bestaudio/best'
                
            ydl_opts.update({
                'format': fmt,
                'outtmpl': os.path.join(folder, '%(title)s.%(ext)s'),
                'merge_output_format': 'mp4',
            })
            
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
                
            if self.stop_flag:
                self.log(">>> Download cancelado pelo usuário.")
                self.after(0, lambda: self.status_label.configure(text="Status: Cancelado", text_color="#D9534F"))
            else:
                self.log(">>> Download concluído com sucesso!")
                self.after(0, lambda: self.status_label.configure(text="Status: Concluído!", text_color="#5CB85C"))
                
        except Exception as e:
            if "Cancelado" in str(e) or self.stop_flag:
                self.log(">>> Download cancelado pelo usuário.")
                self.after(0, lambda: self.status_label.configure(text="Status: Cancelado", text_color="#D9534F"))
            else:
                self.log(f"[Erro] Ocorreu uma falha: {str(e)}")
                self.after(0, lambda: self.status_label.configure(text="Status: Erro no download", text_color="#D9534F"))
                
        finally:
            # Restaura o estado da interface
            def reset_buttons():
                self.start_btn.configure(state="normal")
                self.convert_btn.configure(state="normal")
                self.stop_btn.configure(state="disabled", fg_color="#3E3E56", hover_color="#4F4F6E")
                self.progress_bar.set(0)
                self.percent_label.configure(text="Progresso: 0.0%")
                self.speed_label.configure(text="Velocidade: --")
                self.eta_label.configure(text="Restante: --")
                self.size_label.configure(text="Tamanho: --")
            self.after(0, reset_buttons)
            
    def start_local_conversion(self):
        """Dispara a thread de conversão local para MP4s na pasta selecionada."""
        folder = self.folder_entry.get().strip()
        if not folder or not os.path.exists(folder):
            self.log("[Erro] Por favor, selecione uma pasta de origem válida.")
            return
            
        self.start_btn.configure(state="disabled")
        self.convert_btn.configure(state="disabled")
        self.status_label.configure(text="Status: Convertendo arquivos MP4...", text_color="yellow")
        
        threading.Thread(target=self.local_conversion_worker, args=(folder,), daemon=True).start()
        
    def local_conversion_worker(self, folder):
        """Conversão de arquivos locais MP4 para MP3 utilizando o FFmpeg integrado."""
        self.log("-" * 60)
        self.log(f"Iniciando conversão em lote (MP4 para MP3) na pasta: {folder}")
        
        ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
        mp4_files = [f for f in os.listdir(folder) if f.lower().endswith(".mp4")]
        
        if not mp4_files:
            self.log("Nenhum arquivo MP4 localizado no diretório.")
            self.after(0, lambda: self.status_label.configure(text="Status: Nenhum MP4 encontrado", text_color="gray"))
            self.after(0, lambda: [self.start_btn.configure(state="normal"), self.convert_btn.configure(state="normal")])
            return
            
        total = len(mp4_files)
        success_count = 0
        
        for idx, file in enumerate(mp4_files):
            mp4_path = os.path.join(folder, file)
            mp3_filename = os.path.splitext(file)[0] + ".mp3"
            mp3_path = os.path.join(folder, mp3_filename)
            
            self.log(f"[{idx+1}/{total}] Processando: {file}")
            
            cmd = [
                ffmpeg_exe, '-y',
                '-i', mp4_path,
                '-vn',
                '-acodec', 'libmp3lame',
                '-b:a', '192k',
                mp3_path
            ]
            
            try:
                # Oculta a janela de terminal do FFmpeg no Windows
                startupinfo = None
                if sys.platform == "win32":
                    startupinfo = subprocess.STARTUPINFO()
                    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                    
                result = subprocess.run(
                    cmd, 
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.PIPE, 
                    startupinfo=startupinfo,
                    text=True
                )
                
                if result.returncode == 0:
                    self.log(f"Sucesso: {mp3_filename}")
                    # Remove o original .mp4 como na versão antiga do app
                    try:
                        os.remove(mp4_path)
                        self.log(f"Arquivo original removido: {file}")
                    except Exception as e:
                        self.log(f"[Aviso] Não foi possível apagar o original: {str(e)}")
                    success_count += 1
                else:
                    self.log(f"[Erro] FFmpeg retornou erro para {file}: {result.stderr}")
            except Exception as e:
                self.log(f"[Erro] Falha ao executar FFmpeg: {str(e)}")
                
            # Atualiza o progresso local
            percent = (idx + 1) / total
            self.update_progress_ui(percent, "--", "--", f"{idx+1}/{total} arquivos", file)
            
        self.log(f"Lote concluído! {success_count} de {total} arquivos convertidos.")
        self.after(0, lambda: self.status_label.configure(text=f"Status: {success_count}/{total} Convertidos", text_color="#5CB85C"))
        
        # Restaura botões
        def reset_ui():
            self.start_btn.configure(state="normal")
            self.convert_btn.configure(state="normal")
            self.progress_bar.set(0)
            self.percent_label.configure(text="Progresso: 0.0%")
            self.speed_label.configure(text="Velocidade: --")
            self.eta_label.configure(text="Restante: --")
            self.size_label.configure(text="Tamanho: --")
        self.after(0, reset_ui)

if __name__ == "__main__":
    app = YTDownloaderApp()
    app.mainloop()
