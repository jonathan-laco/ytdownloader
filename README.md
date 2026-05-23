# YouTube Downloader Pro (YTDOWNLOADER) 🚀

Este projeto foi totalmente reestruturado e aprimorado para fornecer a **máxima velocidade de download**, a **melhor qualidade de áudio/vídeo possível** e uma **interface visual moderna e premium (Dark Mode)**. 

Agora, o projeto utiliza as bibliotecas mais recomendadas da indústria, garantindo alta estabilidade contra alterações de código do YouTube.

---

## ✨ Principais Melhorias e Recursos:

1. **Alta Performance com `yt-dlp`**: Substituiu o antigo `pytube` (que apresentava travamentos frequentes). O `yt-dlp` é o motor de download mais rápido e ativamente mantido do mundo.
2. **Integração Automática com FFmpeg (`imageio-ffmpeg`)**: Você **não** precisa instalar o FFmpeg manualmente no seu Windows. O programa instala os binários do FFmpeg de forma interna e o utiliza para fundir o vídeo de alta resolução com o melhor áudio disponível ou para extrair áudios em MP3 de altíssima qualidade (320kbps).
3. **Interface Visual Premium (`customtkinter`)**: Um design escuro moderno, limpo, responsivo, com cantos arredondados, barra de progresso visual, velocidade de download em tempo real (MB/s), tamanho dos arquivos e estimativa de tempo restante (ETA).
4. **Downloads sem Travamentos (Multi-threading)**: O download roda em segundo plano. A interface da janela continua 100% responsiva para que você possa arrastar, ler os logs ou clicar em cancelar.
5. **Suporte Completo a Playlists**: Cole o link de uma playlist completa e o aplicativo baixará todos os vídeos de forma automática e sequencial, mostrando o progresso detalhado.
6. **Cancelamento Rápido**: O botão "Cancelar" interrompe imediatamente qualquer download que esteja em andamento.
7. **Conversão Local de Lote**: Converte em lote todos os vídeos `.mp4` presentes na pasta escolhida para `.mp3` de alta fidelidade usando o FFmpeg embutido de forma rápida.

---

## 🛠️ Pré-requisitos e Instalação

### Passo 1: Instalar as Dependências
Abra o seu terminal (Prompt de Comando ou PowerShell) na pasta do projeto e instale os pacotes necessários:

```bash
pip install -r requirements.txt
```

*(Isso instalará o `yt-dlp`, `customtkinter` e `imageio-ffmpeg` automaticamente).*

---

## 📖 Como Usar o YouTube Downloader Pro

### Passo 2: Executar o Aplicativo
Ainda no terminal na pasta do projeto, execute o script principal:

```bash
python ytdownloader.py
```

A interface moderna escura será aberta imediatamente.

### Passo 3: Configurar e Baixar

1. **Pasta de Salvamento**: 
   - O aplicativo já vem configurado por padrão para salvar os arquivos na pasta **Downloads** do seu Windows (`C:\Users\SeuUsuario\Downloads`).
   - Se quiser alterar, basta clicar no botão **"Escolher Pasta"** e selecionar outro diretório de sua preferência.
2. **Link do YouTube**:
   - Copie o link do vídeo, vídeo Short ou de uma playlist inteira na barra de endereço do seu navegador.
   - Cole no campo **"Link do Vídeo ou Playlist do YouTube"**.
3. **Tipo de Formato**:
   - Selecione **Vídeo (MP4)** se deseja baixar o arquivo com imagem e som.
   - Selecione **Áudio (MP3)** se deseja apenas a música do vídeo. O programa extrairá o áudio e salvará como um arquivo `.mp3` real de 320kbps.
4. **Qualidade Máxima de Vídeo**:
   - Caso tenha escolhido *Vídeo (MP4)*, você pode definir a qualidade limite (ex: `1080p (Full HD)`, `720p (HD)` ou `Melhor Disponível` para baixar em 4K/2K caso disponível).
5. **Iniciar o Download**:
   - Clique em **"INICIAR DOWNLOAD"**.
   - A barra de progresso será atualizada em tempo real junto com a **Velocidade de rede**, o **Tempo Restante** e o **Tamanho do Arquivo**.
   - Os logs detalhados do progresso e do processo de conversão do FFmpeg aparecerão na caixa preta inferior de histórico.

---

## 💡 Dicas de Uso

* **Downloads de Vídeos Individuais vs Playlists**: O programa reconhece o tipo de link sozinho. Se você colocar o link de uma playlist inteira e clicar em "Iniciar Download", os logs mostrarão "Baixando (1/12): Nome do Vídeo..." e passarão para o próximo item automaticamente até baixar tudo.
* **Interrompendo um download**: Se a playlist for muito grande ou o download estiver demorando, clique em **"CANCELAR"**. O programa parará o processo de forma limpa.
* **Conversor MP4 para MP3**: Se você já tem vídeos `.mp4` antigos na pasta de destino e quer convertê-los de forma super rápida para músicas `.mp3`, basta clicar no botão **"CONVERTER MP4 -> MP3"**. Ele processará os arquivos em lote na velocidade máxima usando o FFmpeg.
