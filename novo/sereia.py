import sys
import os
import json
import multiprocessing as mp
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog
from PyQt5.QtCore import Qt, QObject, pyqtSignal, pyqtSlot, QUrl, QThread
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWebChannel import QWebChannel

import nemo
import estrela_do__mar
import cavalo_marinho


# =============================================================================
# Redirecionador de stdout para a interface web
# =============================================================================
class RedirecionadorLog(object):
    """Redireciona os prints para área de log da UI (web)"""
    def __init__(self, sinal):
        self.sinal = sinal

    def write(self, texto):
        if texto.strip():
            self.sinal.emit(texto.strip())

    def flush(self):
        pass


# =============================================================================
# Trabalhador da pipeline 
# =============================================================================
class TrabalhadorPipeline(QThread):
    sinal_log = pyqtSignal(str)
    sinal_concluido = pyqtSignal()

    def __init__(self, arquivo_zst, qtd_partidas):
        super().__init__()
        self.arquivo_zst = arquivo_zst
        self.qtd_partidas = qtd_partidas
        self.diretorio_base = os.path.dirname(os.path.abspath(__file__))

    def run(self):
        caminho_pgn_temporario = os.path.join(self.diretorio_base, "partidas_filtradas.pgn")
        pasta_aberturas = os.path.join(self.diretorio_base, "aberturas_organizadas")
        pasta_csv_saida = self.diretorio_base

        self.sinal_log.emit("🧜‍♀️ Iniciando o Canto da Sereia...")
        self.sinal_log.emit("=" * 40)

        nemo.extrair_partidas_zst(self.arquivo_zst, caminho_pgn_temporario, self.qtd_partidas)
        self.sinal_log.emit("\n")

        estrela_do__mar.separar_pgn_por_abertura(caminho_pgn_temporario, pasta_aberturas)
        self.sinal_log.emit("\n")

        cavalo_marinho.processar_para_csv(pasta_aberturas, pasta_csv_saida)

        self.sinal_log.emit("\n✨ Processo finalizado com sucesso! O oceano de dados está pronto.")
        self.sinal_concluido.emit()


# =============================================================================
# Ponte JavaScript ↔ Python (usando QWebChannel)
# =============================================================================
class Bridge(QObject):
    def __init__(self, app):
        super().__init__()
        self.app = app

    @pyqtSlot()
    def selecionar_arquivo(self):
        """Abre o diálogo de seleção de arquivo e atualiza a UI web"""
        arquivo, _ = QFileDialog.getOpenFileName(
            None, "Selecione o arquivo ZST", "", "Zstandard (*.zst);;Todos os Arquivos (*)"
        )
        if arquivo:
            self.app.arquivo_selecionado = arquivo
            self.app.webview.page().runJavaScript(f"setFilePath({json.dumps(arquivo)})")

    @pyqtSlot(int)
    def iniciar_pipeline(self, qtd_partidas):
        """Inicia a thread de processamento"""
        if not self.app.arquivo_selecionado:
            return  # segurança extra
        self.app.qtd_partidas = qtd_partidas
        self.app.webview.page().runJavaScript("disableControls()")
        self.app.webview.page().runJavaScript("clearLog()")
        self.app.executar_pipeline()


# =============================================================================
# Aplicação principal – Janela com WebEngine e tema marinho
# =============================================================================
class SereiaApp(QMainWindow):
    sinal_de_texto = pyqtSignal(str)  

    def __init__(self):
        super().__init__()
        self.arquivo_selecionado = None
        self.qtd_partidas = 10000

        # Cria o widget de web engine
        self.webview = QWebEngineView()
        self.setCentralWidget(self.webview)

        # Configura o canal e a ponte
        self.canal = QWebChannel()
        self.bridge = Bridge(self)
        self.canal.registerObject("bridge", self.bridge)
        self.webview.page().setWebChannel(self.canal)

        # Carrega a interface HTML maravilhosa
        self.webview.setHtml(self._html_da_sereia())

        # Redireciona o stdout para a interface web
        self.sinal_de_texto.connect(self._log_para_web)
        sys.stdout = RedirecionadorLog(self.sinal_de_texto)

        # Janela
        self.setWindowTitle("Sereia - Orquestrador do Fundo do Mar 🧜‍♀️🌊")
        self.resize(750, 600)

    def _log_para_web(self, texto):
        """Envia uma mensagem de log para a div no HTML"""
        # Escapa aspas para o JavaScript
        safe_text = json.dumps(texto)
        self.webview.page().runJavaScript(f"addLog({safe_text})")

    def executar_pipeline(self):
        """Dispara a thread de processamento e conecta os sinais"""
        self.thread = TrabalhadorPipeline(self.arquivo_selecionado, self.qtd_partidas)
        self.thread.sinal_log.connect(self._log_para_web)
        self.thread.sinal_concluido.connect(self._pipeline_finalizado)
        self.thread.start()

    def _pipeline_finalizado(self):
        """Reabilita os controles quando a pipeline termina"""
        self.webview.page().runJavaScript("enableControls()")

    def _html_da_sereia(self):
        """Retorna o HTML completo com CSS e JavaScript temáticos"""
        return r"""
<!DOCTYPE html>
<html lang="pt">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Sereia</title>
<style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
        font-family: 'Segoe UI', 'Georgia', serif;
        background: radial-gradient(ellipse at bottom, #0d3b4f 0%, #051e2b 100%);
        min-height: 100vh;
        display: flex;
        justify-content: center;
        align-items: center;
        overflow: hidden;
        position: relative;
    }

    /* Ondas no fundo */
    .wave {
        position: absolute;
        bottom: 0;
        left: 0;
        width: 200%;
        height: 120px;
        background: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1440 320"><path fill="%232bbbad" fill-opacity="0.3" d="M0,192L48,197.3C96,203,192,213,288,213.3C384,213,480,203,576,186.7C672,171,768,149,864,160C960,171,1056,213,1152,213.3C1248,213,1344,171,1392,149.3L1440,128L1440,320L1392,320C1344,320,1248,320,1152,320C1056,320,960,320,864,320C768,320,672,320,576,320C480,320,384,320,288,320C192,320,96,320,48,320L0,320Z"/></svg>') repeat-x;
        background-size: 50% 100%;
        animation: waveMove 12s linear infinite;
        z-index: 0;
    }
    .wave:nth-child(2) {
        bottom: 20px;
        opacity: 0.5;
        animation-duration: 18s;
        animation-direction: reverse;
    }
    @keyframes waveMove {
        0% { transform: translateX(0); }
        100% { transform: translateX(-50%); }
    }

    /* Bolhas flutuantes */
    .bubble {
        position: absolute;
        background: rgba(255,255,255,0.15);
        border-radius: 50%;
        box-shadow: 0 0 10px rgba(255, 255, 255, 0.3);
        animation: floatUp 8s infinite ease-in;
        z-index: 1;
    }
    .bubble::after {
        content: "";
        position: absolute;
        top: 15%; left: 20%;
        width: 30%; height: 20%;
        background: rgba(255,255,255,0.6);
        border-radius: 50%;
        transform: rotate(-30deg);
    }
    .bubble:nth-child(3) { left: 10%; width: 40px; height: 40px; animation-duration: 6s; animation-delay: 0s; }
    .bubble:nth-child(4) { left: 30%; width: 25px; height: 25px; animation-duration: 7s; animation-delay: 1s; }
    .bubble:nth-child(5) { left: 55%; width: 50px; height: 50px; animation-duration: 9s; animation-delay: 2s; }
    .bubble:nth-child(6) { left: 75%; width: 30px; height: 30px; animation-duration: 5s; animation-delay: 0.5s; }
    .bubble:nth-child(7) { left: 90%; width: 20px; height: 20px; animation-duration: 8s; animation-delay: 3s; }

    @keyframes floatUp {
        0% { transform: translateY(100vh) scale(0.8); opacity: 0.3; }
        50% { opacity: 0.7; }
        100% { transform: translateY(-10vh) scale(1.2); opacity: 0; }
    }

    /* Painel central vidro */
    .panel {
        position: relative;
        z-index: 10;
        background: rgba(255, 255, 255, 0.08);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border-radius: 20px;
        border: 1px solid rgba(0, 255, 250, 0.3);
        box-shadow: 0 20px 50px rgba(0, 0, 0, 0.5), 0 0 30px rgba(0, 255, 255, 0.2);
        padding: 30px 35px;
        width: 90%;
        max-width: 600px;
        color: #e0f7fa;
        text-align: center;
    }

    h1 {
        font-size: 2.5em;
        margin-bottom: 10px;
        background: linear-gradient(to right, #00e5ff, #76ff03);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0 0 20px #00e5ff;
        animation: glow 2s infinite alternate;
    }
    @keyframes glow {
        0% { text-shadow: 0 0 10px #00e5ff; }
        100% { text-shadow: 0 0 30px #00e5ff, 0 0 60px #76ff03; }
    }

    .file-area {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 10px;
        margin: 20px 0;
        flex-wrap: wrap;
    }
    .file-path {
        background: rgba(0, 0, 0, 0.3);
        padding: 8px 15px;
        border-radius: 30px;
        border: 1px dashed #00bcd4;
        color: #b2ebf2;
        max-width: 250px;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }

    button {
        background: rgba(0, 131, 143, 0.7);
        border: none;
        border-radius: 30px;
        color: white;
        font-weight: bold;
        font-size: 1em;
        padding: 10px 25px;
        cursor: pointer;
        transition: all 0.3s;
        box-shadow: 0 4px 15px rgba(0, 255, 200, 0.3);
        backdrop-filter: blur(5px);
    }
    button:hover {
        background: #00acc1;
        box-shadow: 0 0 25px #00e5ff;
        transform: scale(1.05);
    }
    button:disabled {
        opacity: 0.4;
        cursor: not-allowed;
        box-shadow: none;
    }

    .spin-area {
        margin: 20px 0;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 15px;
    }
    input[type="number"] {
        width: 120px;
        padding: 10px;
        border-radius: 20px;
        border: 2px solid #00838f;
        background: rgba(0,0,0,0.5);
        color: #e0f7fa;
        font-size: 1em;
        text-align: center;
    }

    .log-box {
        margin-top: 25px;
        background: rgba(0, 20, 30, 0.7);
        border-radius: 15px;
        border: 1px solid #26c6da;
        padding: 10px;
        max-height: 200px;
        overflow-y: auto;
        text-align: left;
        font-family: 'Consolas', monospace;
        font-size: 0.9em;
        color: #b2dfdb;
        box-shadow: inset 0 0 20px rgba(0,0,0,0.8);
    }
    .log-entry {
        padding: 3px 5px;
        border-bottom: 1px solid rgba(0, 255, 200, 0.1);
        word-break: break-word;
    }
    .log-box::-webkit-scrollbar {
        width: 8px;
    }
    .log-box::-webkit-scrollbar-track {
        background: #04363e;
        border-radius: 10px;
    }
    .log-box::-webkit-scrollbar-thumb {
        background: #00897b;
        border-radius: 10px;
    }

    /* Rabo de sereia decorativo */
    .mermaid-tail {
        position: absolute;
        bottom: 10px;
        right: 20px;
        z-index: 5;
        opacity: 0.6;
        animation: sway 4s infinite ease-in-out;
    }
    @keyframes sway {
        0%,100% { transform: rotate(-3deg); }
        50% { transform: rotate(5deg); }
    }
</style>
</head>
<body>
    <!-- Ondas decorativas -->
    <div class="wave"></div>
    <div class="wave"></div>

    <!-- Bolhas -->
    <div class="bubble" style="left:10%; animation-delay:0s;"></div>
    <div class="bubble" style="left:30%; animation-delay:1s;"></div>
    <div class="bubble" style="left:55%; animation-delay:2s;"></div>
    <div class="bubble" style="left:75%; animation-delay:0.5s;"></div>
    <div class="bubble" style="left:90%; animation-delay:3s;"></div>

    <!-- Rabo de sereia (SVG) -->
    <div class="mermaid-tail">
        <svg width="100" height="150" viewBox="0 0 100 150" fill="none">
            <path d="M50 150 C20 120, 10 70, 50 20 C90 70, 80 120, 50 150Z" fill="#00897B" opacity="0.8"/>
            <path d="M50 20 C30 50, 30 90, 50 120" stroke="#B2DFDB" stroke-width="2" fill="none"/>
        </svg>
    </div>

    <!-- Painel principal -->
    <div class="panel">
        <h1>🧜‍♀️ Sereia</h1>
        <p style="color:#b2ebf2;">Orquestrador do Fundo do Mar 🌊</p>

        <div class="file-area">
            <button onclick="bridge.selecionar_arquivo()">🐟 Selecionar Arquivo .pgn.zst</button>
            <span id="filePath" class="file-path">Nenhum arquivo selecionado.</span>
        </div>

        <div class="spin-area">
            <label for="qtdPartidas">🐙 Partidas:</label>
            <input type="number" id="qtdPartidas" value="10000" min="1" max="100000000" step="1000">
        </div>

        <button id="btnRun" onclick="executarPipeline()" disabled>🌊 Mergulhar nos Dados</button>

        <div class="log-box" id="logContainer">
            <div class="log-entry">🐚 Diário de Bordo pronto...</div>
        </div>
    </div>

    <script src="qrc:///qtwebchannel/qwebchannel.js"></script>
    <script>
        let bridge = null;
        let channel = new QWebChannel(qt.webChannelTransport, function(ch) {
            bridge = ch.objects.bridge;
            // Habilita o botão de execução se arquivo já foi selecionado (improvável no início)
        });

        // Funções chamadas pelo Python
        function setFilePath(path) {
            document.getElementById('filePath').textContent = path;
            document.getElementById('btnRun').disabled = false;
        }

        function addLog(message) {
            const container = document.getElementById('logContainer');
            const entry = document.createElement('div');
            entry.className = 'log-entry';
            entry.textContent = message;
            container.appendChild(entry);
            container.scrollTop = container.scrollHeight;
        }

        function clearLog() {
            document.getElementById('logContainer').innerHTML = '';
        }

        function disableControls() {
            document.getElementById('btnRun').disabled = true;
            document.querySelectorAll('button').forEach(b => b.disabled = true);
            document.getElementById('qtdPartidas').disabled = true;
        }

        function enableControls() {
            document.getElementById('btnRun').disabled = false;
            document.querySelectorAll('button').forEach(b => b.disabled = false);
            document.getElementById('qtdPartidas').disabled = false;
        }

        function executarPipeline() {
            let qtd = parseInt(document.getElementById('qtdPartidas').value, 10) || 10000;
            bridge.iniciar_pipeline(qtd);
        }
    </script>
</body>
</html>
"""


if __name__ == '__main__':
    mp.freeze_support()
    app = QApplication(sys.argv)
    janela = SereiaApp()
    janela.show()
    sys.exit(app.exec_())
