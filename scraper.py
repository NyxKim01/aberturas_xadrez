import os
import sys
import time
import urllib.parse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QHBoxLayout,
    QFrame,
    QMessageBox,
    QProgressBar,
)

def baixar_partidas_abertura(nome_abertura, callback_status=None):
    def log(msg):
        if callback_status:
            callback_status(msg)
        print(msg)
    pasta_atual = os.getcwd()
    prefs = {
        "download.default_directory": pasta_atual,
        "download.prompt_for_download": False,
        "directory_upgrade": True,
        "safebrowsing.enabled": True,
    }
    options = webdriver.ChromeOptions()
    options.add_experimental_option("prefs", prefs)
    options.add_argument("--start-maximized")
    log(f"♟ Iniciando navegador. Downloads serão salvos em: {pasta_atual}")
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )
    wait = WebDriverWait(driver, 20)
    try:
        nome_formatado = urllib.parse.quote_plus(nome_abertura)
        url_direta = f"https://www.chess.com/games/search?opening={nome_formatado}"
        log(f"♜ Acessando a abertura: {nome_abertura}")
        driver.get(url_direta)
        log("♞ Aguardando a tabela de partidas carregar...")
        checkbox_todos = wait.until(
            EC.presence_of_element_located((By.ID, "master-games-check-all"))
        )
        log("♛ Selecionando todas as partidas da página...")
        driver.execute_script("arguments[0].click();", checkbox_todos)
        log("♚ Clicando no botão de download...")
        botao_baixar = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".master-games-download-button"))
        )
        driver.execute_script("arguments[0].click();", botao_baixar)
        log("⏳ Aguardando o download terminar...")
        time.sleep(5)
        log("✅ Processo concluído com sucesso!")
        return True
    except Exception as e:
        log(f"❌ Ocorreu um erro durante a execução: {e}")
        return False
    finally:
        driver.quit()
        log("🧹 Navegador fechado.")

class DownloadWorker(QThread):
    status = pyqtSignal(str)
    finished_ok = pyqtSignal(bool)
    def __init__(self, abertura):
        super().__init__()
        self.abertura = abertura
    def run(self):
        ok = baixar_partidas_abertura(self.abertura, callback_status=self.status.emit)
        self.finished_ok.emit(ok)

class ChessCuteApp(QWidget):
    def __init__(self):
        super().__init__()
        self.worker = None
        self.init_ui()
    def init_ui(self):
        self.setWindowTitle("♟ Downloader de Aberturas de Xadrez")
        self.setMinimumSize(760, 560)
        self.setStyleSheet("""
            QWidget {
                background-color: #f4efe6;
                color: #2f2a24;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QFrame#Card {
                background-color: #fffaf3;
                border: 2px solid #d9c7aa;
                border-radius: 24px;
            }
            QLabel#Title {
                color: #5a3e2b;
                font-size: 30px;
                font-weight: 800;
            }
            QLabel#Subtitle {
                color: #7a6656;
                font-size: 14px;
            }
            QLabel#SectionLabel {
                color: #5a3e2b;
                font-size: 15px;
                font-weight: 700;
            }
            QLineEdit {
                background: #fff;
                border: 2px solid #d7c4ab;
                border-radius: 14px;
                padding: 12px 14px;
                font-size: 15px;
                color: #2f2a24;
            }
            QLineEdit:focus {
                border: 2px solid #8b6b4f;
            }
            QPushButton {
                background-color: #7b5e3b;
                color: white;
                border: none;
                border-radius: 16px;
                padding: 12px 18px;
                font-size: 15px;
                font-weight: 700;
            }
            QPushButton:hover {
                background-color: #8c6b45;
            }
            QPushButton:disabled {
                background-color: #c8b6a0;
                color: #f8f3ec;
            }
            QTextEdit {
                background-color: #fff;
                border: 2px solid #d7c4ab;
                border-radius: 16px;
                padding: 10px;
                font-size: 13px;
                color: #3a3129;
            }
            QProgressBar {
                border: 2px solid #d7c4ab;
                border-radius: 10px;
                text-align: center;
                background-color: #fff;
                height: 20px;
                font-weight: 700;
            }
            QProgressBar::chunk {
                background-color: #7b5e3b;
                border-radius: 8px;
            }
        """)
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(18)
        card = QFrame()
        card.setObjectName("Card")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(28, 28, 28, 28)
        card_layout.setSpacing(16)
        title = QLabel("♟ Downloader de Aberturas")
        title.setObjectName("Title")
        title.setAlignment(Qt.AlignCenter)
        subtitle = QLabel("Há dois tipos de sacrifícios: os corretos e os meus.")
        subtitle.setObjectName("Subtitle")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setWordWrap(True)
        header = QVBoxLayout()
        header.addWidget(title)
        header.addWidget(subtitle)
        label = QLabel("Nome da abertura")
        label.setObjectName("SectionLabel")
        self.input_abertura = QLineEdit()
        self.input_abertura.setPlaceholderText("Ex: Ruy Lopez, Sicilian Defense, Queen's Gambit...")
        self.input_abertura.returnPressed.connect(self.iniciar_download)
        self.botao = QPushButton("Baixar partidas ♜")
        self.botao.clicked.connect(self.iniciar_download)
        self.status = QLabel("Pronto para começar. Escolha uma abertura e clique no botão.")
        self.status.setWordWrap(True)
        self.progresso = QProgressBar()
        self.progresso.setRange(0, 0)
        self.progresso.hide()
        botoes_linha = QHBoxLayout()
        botoes_linha.addStretch()
        botoes_linha.addWidget(self.botao)
        botoes_linha.addStretch()
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setPlaceholderText("Os eventos aparecerão aqui...")
        card_layout.addLayout(header)
        card_layout.addSpacing(6)
        card_layout.addWidget(label)
        card_layout.addWidget(self.input_abertura)
        card_layout.addLayout(botoes_linha)
        card_layout.addWidget(self.progresso)
        card_layout.addWidget(self.status)
        card_layout.addWidget(self.log)
        root.addStretch()
        root.addWidget(card)
        root.addStretch()
        self.input_abertura.setFont(QFont("Segoe UI", 11))
        self.log.setFont(QFont("Consolas", 10))
    def escrever_log(self, texto):
        self.log.append(texto)
    def iniciar_download(self):
        abertura = self.input_abertura.text().strip()
        if not abertura:
            QMessageBox.warning(self, "Atenção", "Digite o nome de uma abertura primeiro.")
            return
        self.botao.setEnabled(False)
        self.input_abertura.setEnabled(False)
        self.progresso.show()
        self.status.setText("Abrindo o navegador e preparando o download...")
        self.escrever_log(f"▶ Iniciando busca para: {abertura}")
        self.worker = DownloadWorker(abertura)
        self.worker.status.connect(self.atualizar_status)
        self.worker.finished_ok.connect(self.finalizar_download)
        self.worker.start()
    def atualizar_status(self, msg):
        self.status.setText(msg)
        self.escrever_log(msg)
    def finalizar_download(self, ok):
        self.progresso.hide()
        self.botao.setEnabled(True)
        self.input_abertura.setEnabled(True)
        if ok:
            self.status.setText("Download finalizado com sucesso!")
            self.escrever_log("🎉 Tudo certo, partidas baixadas.")
            QMessageBox.information(self, "Concluído", "As partidas foram baixadas com sucesso!")
        else:
            self.status.setText("Não foi possível concluir o download.")
            self.escrever_log("⚠ Falha ao baixar as partidas.")
            QMessageBox.critical(self, "Erro", "Não foi possível concluir o download.")
        self.worker = None

if __name__ == "__main__":
    app = QApplication(sys.argv)
    janela = ChessCuteApp()
    janela.show()
    sys.exit(app.exec_())
