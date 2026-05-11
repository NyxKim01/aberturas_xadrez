import sys
import os
import time
import multiprocessing as mp
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QFileDialog, QSpinBox, QTextEdit)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QIcon

import nemo
import estrela_do__mar
import cavalo_marinho

class RedirecionadorLog(object):
    """Redireciona o sys.stdout (os prints) para a interface gráfica"""
    def __init__(self, sinal):
        self.sinal = sinal

    def write(self, texto):
        if texto.strip():
            self.sinal.emit(texto.strip())

    def flush(self):
        pass

class TrabalhadorPipeline(QThread):
    """Roda os scripts em segundo plano para não congelar a interface"""
    sinal_log = pyqtSignal(str)
    sinal_concluido = pyqtSignal()

    def __init__(self, arquivo_zst, qtd_partidas):
        super().__init__()
        self.arquivo_zst = arquivo_zst
        self.qtd_partidas = qtd_partidas
        self.diretorio_base = os.path.dirname(os.path.abspath(__file__))

    def run(self):
        # Configurando caminhos relativos ao script principal
        caminho_pgn_temporario = os.path.join(self.diretorio_base, "partidas_filtradas.pgn")
        pasta_aberturas = os.path.join(self.diretorio_base, "aberturas_organizadas")
        pasta_csv_saida = self.diretorio_base # O csv cria a subpasta internamente

        self.sinal_log.emit("🧜‍♀️ Iniciando o Canto da Sereia...")
        self.sinal_log.emit("="*40)
        
        # 1. Nemo
        nemo.extrair_partidas_zst(self.arquivo_zst, caminho_pgn_temporario, self.qtd_partidas)
        self.sinal_log.emit("\n")
        
        # 2. Estrela do Mar
        estrela_do__mar.separar_pgn_por_abertura(caminho_pgn_temporario, pasta_aberturas)
        self.sinal_log.emit("\n")
        
        # 3. Cavalo Marinho
        cavalo_marinho.processar_para_csv(pasta_aberturas, pasta_csv_saida)
        
        self.sinal_log.emit("\n✨ Processo finalizado com sucesso! O oceano de dados está pronto.")
        self.sinal_concluido.emit()

class SereiaApp(QWidget):
    sinal_de_texto = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.arquivo_selecionado = None
        self.initUI()
        
        # Conecta o sinal personalizado ao log e redireciona stdout
        self.sinal_de_texto.connect(self.atualizar_log)
        sys.stdout = RedirecionadorLog(self.sinal_de_texto)

    def initUI(self):
        self.setWindowTitle("Sereia - Orquestrador do Fundo do Mar 🧜‍♀️🌊")
        self.resize(650, 500)
        
        # Estilo "Fundo do Mar"
        self.setStyleSheet("""
            QWidget {
                background-color: #0B2B40; /* Azul profundo */
                color: #E0F7FA; /* Ciano clarinho */
                font-family: 'Segoe UI', Arial;
            }
            QPushButton {
                background-color: #008B8B; /* Dark Cyan */
                border-radius: 8px;
                padding: 10px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover { background-color: #20B2AA; }
            QPushButton:disabled { background-color: #37474F; color: #78909C; }
            QTextEdit {
                background-color: #041421;
                border: 1px solid #20B2AA;
                border-radius: 5px;
                padding: 5px;
                font-family: Consolas, monospace;
            }
            QLabel { font-size: 13px; font-weight: bold; }
            QSpinBox {
                background-color: #041421;
                border: 1px solid #20B2AA;
                padding: 5px;
                border-radius: 4px;
            }
        """)

        layout_principal = QVBoxLayout()

        # Seleção de Arquivo
        layout_arquivo = QHBoxLayout()
        self.btn_arquivo = QPushButton("🐟 Selecionar Arquivo .pgn.zst")
        self.btn_arquivo.clicked.connect(self.selecionar_arquivo)
        self.lbl_arquivo = QLabel("Nenhum arquivo selecionado.")
        self.lbl_arquivo.setWordWrap(True)
        layout_arquivo.addWidget(self.btn_arquivo)
        layout_arquivo.addWidget(self.lbl_arquivo, 1)
        layout_principal.addLayout(layout_arquivo)

        # Número de Partidas
        layout_partidas = QHBoxLayout()
        self.lbl_partidas = QLabel("🐙 Número de Partidas (X):")
        self.spin_partidas = QSpinBox()
        self.spin_partidas.setRange(1, 100000000)
        self.spin_partidas.setValue(10000)
        self.spin_partidas.setSingleStep(1000)
        layout_partidas.addWidget(self.lbl_partidas)
        layout_partidas.addWidget(self.spin_partidas, 1)
        layout_principal.addLayout(layout_partidas)

        # Botão Rodar
        self.btn_rodar = QPushButton("🌊 Mergulhar nos Dados (Rodar Pipeline)")
        self.btn_rodar.clicked.connect(self.rodar_pipeline)
        self.btn_rodar.setEnabled(False) # Só habilita com arquivo selecionado
        layout_principal.addWidget(self.btn_rodar)

        # Log Console
        self.lbl_log = QLabel("🐚 Diário de Bordo (Logs):")
        layout_principal.addWidget(self.lbl_log)
        self.caixa_log = QTextEdit()
        self.caixa_log.setReadOnly(True)
        layout_principal.addWidget(self.caixa_log)

        self.setLayout(layout_principal)

    def selecionar_arquivo(self):
        arquivo, _ = QFileDialog.getOpenFileName(self, "Selecione o arquivo ZST", "", "Zstandard (*.zst);;Todos Arquivos (*)")
        if arquivo:
            self.arquivo_selecionado = arquivo
            self.lbl_arquivo.setText(arquivo)
            self.btn_rodar.setEnabled(True)

    def atualizar_log(self, texto):
        self.caixa_log.append(texto)

    def rodar_pipeline(self):
        qtd = self.spin_partidas.value()
        self.btn_rodar.setEnabled(False)
        self.btn_arquivo.setEnabled(False)
        self.caixa_log.clear()
        
        # Inicia a thread
        self.thread = TrabalhadorPipeline(self.arquivo_selecionado, qtd)
        self.thread.sinal_concluido.connect(self.pipeline_finalizado)
        self.thread.start()

    def pipeline_finalizado(self):
        self.btn_rodar.setEnabled(True)
        self.btn_arquivo.setEnabled(True)

if __name__ == '__main__':
    mp.freeze_support() # Previne problemas com multiprocessing no Windows
    app = QApplication(sys.argv)
    ex = SereiaApp()
    ex.show()
    sys.exit(app.exec_())