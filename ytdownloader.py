import os
import sys
import threading
import subprocess
import customtkinter as ctk
from tkinter import filedialog
import yt_dlp
import imageio_ffmpeg

# Configuração global de aparência
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class YTDownloaderApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Configuração da Janela Principal
        self.title("YouTube Downloader Pro")
        self.geometry("800x750")
        self.resizable(True, True)
        self.configure(fg_color="#0D0D12") # Fundo azul escuro profundo (mockup)
        
        # Controle de Estado
        self.stop_flag = False
        self.download_thread = None
        
        # Diretório padrão
        self.default_dir = os.path.join(os.path.expanduser("~"), "Downloads")
        if not os.path.exists(self.default_dir):
            self.default_dir = os.getcwd()
            
        self.create_widgets()
        
    def create_widgets(self):
        # Configuração do Grid Principal
        self.grid_rowconfigure((0, 1, 2, 3, 4, 5, 6, 7), weight=0)
        self.grid_rowconfigure(8, weight=1) # A caixa de logs expande verticalmente
        self.grid_columnconfigure(0, weight=1)
        
        # --- 1. CABEÇALHO ---
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, padx=25, pady=(25, 10), sticky="ew")
        
        title_label = ctk.CTkLabel(
            header_frame, 
            text="YouTube Downloader Pro", 
            font=ctk.CTkFont(family="Segoe UI", size=28, weight="bold"),
            text_color="#FF2A54" # Rosa neon estiloso
        )
        title_label.pack(anchor="w")
        
        subtitle_label = ctk.CTkLabel(
            header_frame, 
            text="Baixe playlists e vídeos na velocidade máxima com conversão automática inteligente.", 
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color="#8F8F9F"
        )
        subtitle_label.pack(anchor="w", pady=(2, 0))
        
        # Separador estético moderno
        sep = ctk.CTkFrame(self, height=2, fg_color="#1E1E2E")
        sep.grid(row=1, column=0, padx=25, pady=5, sticky="ew")
        
        # --- 2. SELEÇÃO DA PASTA DE SALVAMENTO ---
        folder_frame = ctk.CTkFrame(self, fg_color="transparent")
        folder_frame.grid(row=2, column=0, padx=25, pady=10, sticky="ew")
        folder_frame.grid_columnconfigure(0, weight=1)
        
        folder_label = ctk.CTkLabel(
            folder_frame, 
            text="Pasta de Salvamento", 
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color="#DFDFEF"
        )
        folder_label.grid(row=0, column=0, sticky="w", pady=(0, 5))
        
        self.folder_entry = ctk.CTkEntry(
            folder_frame, 
            placeholder_text="Selecione onde salvar...",
            fg_color="#151522",
            border_color="#252538",
            border_width=1,
            corner_radius=10,
            text_color="#FFFFFF",
            placeholder_text_color="#555566",
            height=38
        )
        self.folder_entry.grid(row=1, column=0, sticky="ew", padx=(0, 12))
        self.folder_entry.insert(0, self.default_dir)
        
        browse_btn = ctk.CTkButton(
            folder_frame, 
            text="Escolher Pasta", 
            width=130,
            height=38,
            fg_color="#1C1C2D",
            hover_color="#2C2C3E",
            border_color="#3A3A4F",
            border_width=1,
            corner_radius=10,
            text_color="#DFDFEF",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            command=self.browse_folder
        )
        browse_btn.grid(row=1, column=1, sticky="e")
        
        # --- 3. URL ---
        url_frame = ctk.CTkFrame(self, fg_color="transparent")
        url_frame.grid(row=3, column=0, padx=25, pady=10, sticky="ew")
        url_frame.grid_columnconfigure(0, weight=1)
        
        url_label = ctk.CTkLabel(
            url_frame, 
            text="Link do Vídeo ou Playlist do YouTube", 
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color="#DFDFEF"
        )
        url_label.grid(row=0, column=0, sticky="w", pady=(0, 5))
        
        self.url_entry = ctk.CTkEntry(
            url_frame, 
            placeholder_text="Cole o link aqui (Ex: https://www.youtube.com/watch?v=... ou link de playlist)",
            fg_color="#151522",
            border_color="#252538",
            border_width=1,
            corner_radius=10,
            text_color="#FFFFFF",
            placeholder_text_color="#555566",
            height=38
        )
        self.url_entry.grid(row=1, column=0, sticky="ew")
        
        # --- 4. PAINEL DE CONFIGURAÇÕES (Tipo e Qualidade) ---
        settings_frame = ctk.CTkFrame(self, fg_color="#151522", border_width=1, border_color="#252538", corner_radius=12)
        settings_frame.grid(row=4, column=0, padx=25, pady=12, sticky="ew")
        settings_frame.grid_columnconfigure((0, 1), weight=1)
        
        # Tipo de Download
        type_subframe = ctk.CTkFrame(settings_frame, fg_color="transparent")
        type_subframe.grid(row=0, column=0, padx=20, pady=18, sticky="nsew")
        
        type_label = ctk.CTkLabel(
            type_subframe, 
            text="Formato de Saída", 
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color="#DFDFEF"
        )
        type_label.pack(anchor="w", pady=(0, 6))
        
        self.type_segmented = ctk.CTkSegmentedButton(
            type_subframe,
            values=["Vídeo (MP4)", "Áudio (MP3)"],
            selected_color="#FF2A54",
            selected_hover_color="#D61A3F",
            unselected_color="#1C1C2D",
            unselected_hover_color="#2C2C3E",
            corner_radius=8,
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            command=self.toggle_quality_menu,
            height=36
        )
        self.type_segmented.pack(fill="x")
        self.type_segmented.set("Vídeo (MP4)")
        
        # Opções de Qualidade
        quality_subframe = ctk.CTkFrame(settings_frame, fg_color="transparent")
        quality_subframe.grid(row=0, column=1, padx=20, pady=18, sticky="nsew")
        
        quality_label = ctk.CTkLabel(
            quality_subframe, 
            text="Qualidade de Vídeo", 
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color="#DFDFEF"
        )
        quality_label.pack(anchor="w", pady=(0, 6))
        
        self.quality_option = ctk.CTkOptionMenu(
            quality_subframe,
            values=["Melhor Disponível", "1080p (Full HD)", "720p (HD)", "480p (SD)"],
            fg_color="#1C1C2D",
            button_color="#2C2C3E",
            button_hover_color="#3A3A4F",
            dropdown_fg_color="#151522",
            dropdown_hover_color="#2C2C3E",
            dropdown_text_color="#FFFFFF",
            corner_radius=8,
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            height=36
        )
        self.quality_option.pack(fill="x")
        
        # --- 5. PAINEL DE PROGRESSO ---
        self.progress_frame = ctk.CTkFrame(self, fg_color="#151522", border_width=1, border_color="#252538", corner_radius=12)
        self.progress_frame.grid(row=5, column=0, padx=25, pady=12, sticky="ew")
        self.progress_frame.grid_columnconfigure((0, 1), weight=1)
        
        self.status_label = ctk.CTkLabel(
            self.progress_frame, 
            text="Status: Aguardando link...", 
            font=ctk.CTkFont(family="Segoe UI", size=12, slant="italic"),
            text_color="#8F8F9F"
        )
        self.status_label.grid(row=0, column=0, columnspan=2, padx=20, pady=(15, 6), sticky="w")
        
        # Barra de progresso brilhante estilo neon
        self.progress_bar = ctk.CTkProgressBar(
            self.progress_frame, 
            height=14, 
            progress_color="#FF2A54",
            fg_color="#0F0F16",
            corner_radius=7
        )
        self.progress_bar.grid(row=1, column=0, columnspan=2, padx=20, pady=6, sticky="ew")
        self.progress_bar.set(0)
        
        self.percent_label = ctk.CTkLabel(
            self.progress_frame, 
            text="Progresso: 0.0%", 
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color="#FFFFFF"
        )
        self.percent_label.grid(row=2, column=0, padx=20, pady=(6, 15), sticky="w")
        
        stats_subframe = ctk.CTkFrame(self.progress_frame, fg_color="transparent")
        stats_subframe.grid(row=2, column=1, padx=20, pady=(6, 15), sticky="e")
        
        self.speed_label = ctk.CTkLabel(stats_subframe, text="Velocidade: --", font=ctk.CTkFont(family="Segoe UI", size=12), text_color="#8F8F9F")
        self.speed_label.pack(side="left", padx=12)
        
        self.eta_label = ctk.CTkLabel(stats_subframe, text="Restante: --", font=ctk.CTkFont(family="Segoe UI", size=12), text_color="#8F8F9F")
        self.eta_label.pack(side="left", padx=12)
        
        self.size_label = ctk.CTkLabel(stats_subframe, text="Tamanho: --", font=ctk.CTkFont(family="Segoe UI", size=12), text_color="#8F8F9F")
        self.size_label.pack(side="left", padx=12)
        
        # --- 6. BOTÕES DE AÇÃO ---
        actions_frame = ctk.CTkFrame(self, fg_color="transparent")
        actions_frame.grid(row=6, column=0, padx=25, pady=12, sticky="ew")
        actions_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        self.start_btn = ctk.CTkButton(
            actions_frame, 
            text="INICIAR DOWNLOAD", 
            fg_color="#FF2A54",
            hover_color="#D61A3F",
            height=45,
            corner_radius=10,
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            command=self.start_download
        )
        self.start_btn.grid(row=0, column=0, padx=(0, 6), sticky="ew")
        
        self.stop_btn = ctk.CTkButton(
            actions_frame, 
            text="CANCELAR", 
            fg_color="#2C2C3E",
            hover_color="#3E3E56",
            height=45,
            corner_radius=10,
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            state="disabled",
            command=self.stop_download
        )
        self.stop_btn.grid(row=0, column=1, padx=6, sticky="ew")
        
        self.convert_btn = ctk.CTkButton(
            actions_frame, 
            text="CONVERTER MP4 ➔ MP3", 
            fg_color="#1C1C2D",
            hover_color="#2C2C3E",
            border_color="#3A3A4F",
            border_width=1,
            height=45,
            corner_radius=10,
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            command=self.start_local_conversion
        )
        self.convert_btn.grid(row=0, column=2, padx=(6, 0), sticky="ew")
        
        # --- 7. TÍTULO DO TERMINAL DE LOGS ---
        log_frame = ctk.CTkFrame(self, fg_color="transparent")
        log_frame.grid(row=7, column=0, padx=25, pady=(15, 6), sticky="ew")
        
        log_title = ctk.CTkLabel(
            log_frame, 
            text="Terminal de Logs em Tempo Real", 
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color="#DFDFEF"
        )
        log_title.pack(side="left")
        
        clear_log_btn = ctk.CTkButton(
            log_frame,
            text="Limpar logs",
            width=90,
            height=22,
            fg_color="transparent",
            text_color="#8F8F9F",
            hover_color="#1C1C2D",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            command=self.clear_logs
        )
        clear_log_btn.pack(side="right")
        
        # --- 8. ÁREA DO TERMINAL DE LOGS (Estilo Hacker Cyberpunk) ---
        self.log_textbox = ctk.CTkTextbox(
            self,
            font=ctk.CTkFont(family="Consolas", size=11),
            fg_color="#07070C", # Fundo preto puro de terminal
            text_color="#00FFC4", # Texto ciano brilhante estilo hacker
            border_width=1,
            border_color="#202030",
            corner_radius=12
        )
        self.log_textbox.grid(row=8, column=0, padx=25, pady=(0, 25), sticky="nsew")
        self.log_textbox.configure(state="disabled")
        
        # Log Inicial
        self.log(">>> [SISTEMA] YouTube Downloader Pro Inicializado com Sucesso.")
        self.log(">>> [INFO] FFmpeg integrado nativamente para conversão sem perdas.")
        
    def log(self, message):
        """Adiciona mensagens ao console de logs garantindo a sincronia da thread UI."""
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
        self.log(">>> Logs limpos.")
        
    def browse_folder(self):
        folder = filedialog.askdirectory(initialdir=self.folder_entry.get())
        if folder:
            self.folder_entry.delete(0, "end")
            self.folder_entry.insert(0, folder)
            self.log(f"[DIRETÓRIO] Pasta de destino atualizada: {folder}")
            
    def toggle_quality_menu(self, selection):
        if selection == "Áudio (MP3)":
            self.quality_option.configure(state="disabled")
        else:
            self.quality_option.configure(state="normal")
            
    def update_progress_ui(self, percent, speed_str, eta_str, size_str, filename, playlist_index=None, playlist_count=None):
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
            self.status_label.configure(text=status, text_color="#FFFFFF")
        self.after(0, run_in_main)
        
    def start_download(self):
        url = self.url_entry.get().strip()
        folder = self.folder_entry.get().strip()
        
        if not url:
            self.log("[ERRO] Por favor, insira o link do YouTube.")
            return
        if not folder:
            self.log("[ERRO] Por favor, defina a pasta de salvamento.")
            return
            
        if not os.path.exists(folder):
            try:
                os.makedirs(folder, exist_ok=True)
                self.log(f"[SISTEMA] Criando diretório de salvamento: {folder}")
            except Exception as e:
                self.log(f"[ERRO] Falha ao criar diretório: {str(e)}")
                return
                
        self.stop_flag = False
        download_type = self.type_segmented.get()
        quality = self.quality_option.get()
        
        # Desativa interações paralelas
        self.start_btn.configure(state="disabled")
        self.convert_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal", fg_color="#D9534F", hover_color="#C9302C")
        
        self.status_label.configure(text="Status: Conectando aos servidores do YouTube...", text_color="#FFCC00")
        
        self.download_thread = threading.Thread(
            target=self.download_worker, 
            args=(url, folder, download_type, quality), 
            daemon=True
        )
        self.download_thread.start()
        
    def stop_download(self):
        self.stop_flag = True
        self.log("[SISTEMA] Cancelamento acionado. Parando threads de download...")
        self.stop_btn.configure(state="disabled")
        
    def download_worker(self, url, folder, download_type, quality):
        self.log("=" * 60)
        self.log(f"[DOWNLOAD] Iniciando fila de tarefas...")
        self.log(f"[LINK] {url}")
        self.log(f"[FORMATO] {download_type}")
        if download_type == "Vídeo (MP4)":
            self.log(f"[QUALIDADE] Limite selecionado: {quality}")
            
        def progress_hook(d):
            if self.stop_flag:
                raise Exception("Cancelado pelo usuário")
                
            if d['status'] == 'downloading':
                downloaded = d.get('downloaded_bytes', 0)
                total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
                speed = d.get('speed')
                eta = d.get('eta')
                
                percent = downloaded / total if total and total > 0 else 0
                
                if speed:
                    if speed > 1024 * 1024:
                        speed_str = f"{speed / (1024*1024):.2f} MB/s"
                    else:
                        speed_str = f"{speed / 1024:.2f} KB/s"
                else:
                    speed_str = "-- KB/s"
                    
                eta_str = f"{eta}s" if eta else "--s"
                
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
                self.update_progress_ui(1.0, "0.0 B/s", "0s", "Concluído", "Finalizando conversão/fusão...", None, None)
                
        class YtdlLogger:
            def __init__(self, app):
                self.app = app
            def debug(self, msg):
                if not any(x in msg for x in ["[download] ", "[download]  ", "%"]):
                    self.app.log(f"[YT-DLP] {msg}")
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
        
        # MP3 Audio
        if download_type == "Áudio (MP3)":
            ydl_opts.update({
                'format': 'bestaudio/best',
                'outtmpl': os.path.join(folder, '%(title)s.%(ext)s'),
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '320', # Extração direta em 320kbps
                }],
            })
        else:
            # MP4 Video
            if quality == "1080p (Full HD)":
                fmt = 'bestvideo[height<=1080]+bestaudio/best'
            elif quality == "720p (HD)":
                fmt = 'bestvideo[height<=720]+bestaudio/best'
            elif quality == "480p (SD)":
                fmt = 'bestvideo[height<=480]+bestaudio/best'
            else:
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
                self.log(">>> [DOWNLOAD] Cancelado com sucesso pelo usuário.")
                self.after(0, lambda: self.status_label.configure(text="Status: Cancelado", text_color="#D9534F"))
            else:
                self.log(">>> [DOWNLOAD] Todos os arquivos processados com sucesso!")
                self.after(0, lambda: self.status_label.configure(text="Status: Concluído!", text_color="#5CB85C"))
                
        except Exception as e:
            if "Cancelado" in str(e) or self.stop_flag:
                self.log(">>> [DOWNLOAD] Cancelado com sucesso pelo usuário.")
                self.after(0, lambda: self.status_label.configure(text="Status: Cancelado", text_color="#D9534F"))
            else:
                self.log(f"[ERRO] Ocorreu uma falha no download: {str(e)}")
                self.after(0, lambda: self.status_label.configure(text="Status: Erro no download", text_color="#D9534F"))
                
        finally:
            def reset_buttons():
                self.start_btn.configure(state="normal")
                self.convert_btn.configure(state="normal")
                self.stop_btn.configure(state="disabled", fg_color="#2C2C3E", hover_color="#3E3E56")
                self.progress_bar.set(0)
                self.percent_label.configure(text="Progresso: 0.0%")
                self.speed_label.configure(text="Velocidade: --")
                self.eta_label.configure(text="Restante: --")
                self.size_label.configure(text="Tamanho: --")
            self.after(0, reset_buttons)
            
    def start_local_conversion(self):
        folder = self.folder_entry.get().strip()
        if not folder or not os.path.exists(folder):
            self.log("[ERRO] Pasta de origem inválida.")
            return
            
        self.start_btn.configure(state="disabled")
        self.convert_btn.configure(state="disabled")
        self.status_label.configure(text="Status: Convertendo MP4s locais...", text_color="#FFCC00")
        
        threading.Thread(target=self.local_conversion_worker, args=(folder,), daemon=True).start()
        
    def local_conversion_worker(self, folder):
        self.log("=" * 60)
        self.log(f"[CONVERSÃO LOCAL] Iniciando conversão de .mp4 para .mp3 em: {folder}")
        
        ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
        mp4_files = [f for f in os.listdir(folder) if f.lower().endswith(".mp4")]
        
        if not mp4_files:
            self.log("[SISTEMA] Nenhum arquivo .mp4 encontrado na pasta.")
            self.after(0, lambda: self.status_label.configure(text="Status: Nenhum MP4 encontrado", text_color="gray"))
            self.after(0, lambda: [self.start_btn.configure(state="normal"), self.convert_btn.configure(state="normal")])
            return
            
        total = len(mp4_files)
        success_count = 0
        
        for idx, file in enumerate(mp4_files):
            mp4_path = os.path.join(folder, file)
            mp3_filename = os.path.splitext(file)[0] + ".mp3"
            mp3_path = os.path.join(folder, mp3_filename)
            
            self.log(f"[{idx+1}/{total}] Convertendo: {file}")
            
            cmd = [
                ffmpeg_exe, '-y',
                '-i', mp4_path,
                '-vn',
                '-acodec', 'libmp3lame',
                '-b:a', '192k',
                mp3_path
            ]
            
            try:
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
                    self.log(f"[SUCESSO] Salvo como: {mp3_filename}")
                    try:
                        os.remove(mp4_path)
                        self.log(f"[SISTEMA] Apagado arquivo original .mp4.")
                    except Exception as e:
                        self.log(f"[AVISO] Não foi possível apagar o original: {str(e)}")
                    success_count += 1
                else:
                    self.log(f"[ERRO] Falha FFmpeg para {file}: {result.stderr}")
            except Exception as e:
                self.log(f"[ERRO] Falha ao executar subprocesso: {str(e)}")
                
            percent = (idx + 1) / total
            self.update_progress_ui(percent, "--", "--", f"{idx+1}/{total} arquivos", file)
            
        self.log(f"[CONVERSÃO LOCAL] Finalizado. {success_count} de {total} arquivos convertidos.")
        self.after(0, lambda: self.status_label.configure(text=f"Status: {success_count}/{total} Convertidos", text_color="#5CB85C"))
        
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
