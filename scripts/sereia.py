import sys
import os
import multiprocessing as mp
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QFileDialog, QSpinBox, QTextEdit, QCheckBox)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import nemo
import estrela_do_mar
import cavalo_marinho

class RedirecionadorLog(object):
    def __init__(self, sinal):
        self.sinal = sinal
    def write(self, texto):
        if texto.strip():
            self.sinal.emit(texto.strip())
    def flush(self):
        pass

class TrabalhadorPipeline(QThread):
    sinal_log = pyqtSignal(str)
    sinal_concluido = pyqtSignal()
    def __init__(self, arquivo_zst, qtd_partidas, max_dif_rating, usar_probabilidade):
        super().__init__()
        self.arquivo_zst = arquivo_zst
        self.qtd_partidas = qtd_partidas
        self.max_dif_rating = max_dif_rating
        self.usar_probabilidade = usar_probabilidade
        self.diretorio_base = os.path.dirname(os.path.abspath(__file__))
    def run(self):
        caminho_pgn_temporario = os.path.join(self.diretorio_base, "partidas_filtradas.pgn")
        pasta_aberturas = os.path.join(self.diretorio_base, "aberturas_organizadas")
        pasta_csv_saida = self.diretorio_base 
        self.sinal_log.emit("🧜‍♀️ Iniciando o Canto da Sereia...")
        self.sinal_log.emit("="*40)
        nemo.extrair_partidas_zst(
            self.arquivo_zst, 
            caminho_pgn_temporario, 
            self.qtd_partidas, 
            self.max_dif_rating, 
            self.usar_probabilidade
        )
        self.sinal_log.emit("\n")
        estrela_do__mar.separar_pgn_por_abertura(caminho_pgn_temporario, pasta_aberturas)
        self.sinal_log.emit("\n")
        cavalo_marinho.processar_para_csv(pasta_aberturas, pasta_csv_saida)
        self.sinal_log.emit("\n✨ Processo finalizado com sucesso! O oceano de dados está pronto.")
        self.sinal_concluido.emit()

class SereiaApp(QWidget):
    sinal_de_texto = pyqtSignal(str)
    def __init__(self):
        super().__init__()
        self.arquivo_selecionado = None
        self.initUI()
        self.sinal_de_texto.connect(self.atualizar_log)
        sys.stdout = RedirecionadorLog(self.sinal_de_texto)
    def initUI(self):
        self.setWindowTitle("Sereia - Orquestrador do Fundo do Mar 🧜‍♀️🌊")
        self.resize(650, 550)
        self.setStyleSheet("""
            QWidget {
                background-color: #0B2B40; 
                color: #E0F7FA; 
                font-family: 'Segoe UI', Arial;
            }
            QPushButton {
                background-color: #008B8B; 
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
                color: #E0F7FA;
            }
            QCheckBox {
                font-size: 13px; 
                font-weight: bold;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 1px solid #20B2AA;
                background-color: #041421;
                border-radius: 3px;
            }
            QCheckBox::indicator:checked {
                background-color: #20B2AA;
            }
        """)
        layout_principal = QVBoxLayout()
        layout_arquivo = QHBoxLayout()
        self.btn_arquivo = QPushButton("🐟 Selecionar Arquivo .pgn.zst")
        self.btn_arquivo.clicked.connect(self.selecionar_arquivo)
        self.lbl_arquivo = QLabel("Nenhum arquivo selecionado.")
        self.lbl_arquivo.setWordWrap(True)
        layout_arquivo.addWidget(self.btn_arquivo)
        layout_arquivo.addWidget(self.lbl_arquivo, 1)
        layout_principal.addLayout(layout_arquivo)
        layout_configs = QHBoxLayout()
        self.lbl_partidas = QLabel("🐙 Partidas (X):")
        self.spin_partidas = QSpinBox()
        self.spin_partidas.setRange(1, 100000000)
        self.spin_partidas.setValue(10000)
        self.spin_partidas.setSingleStep(1000)
        self.lbl_dif_rating = QLabel("⚖️ Max Dif. Rating:")
        self.spin_dif_rating = QSpinBox()
        self.spin_dif_rating.setRange(0, 3000)
        self.spin_dif_rating.setValue(200)
        self.spin_dif_rating.setSingleStep(50)
        layout_configs.addWidget(self.lbl_partidas)
        layout_configs.addWidget(self.spin_partidas, 1)
        layout_configs.addSpacing(20)
        layout_configs.addWidget(self.lbl_dif_rating)
        layout_configs.addWidget(self.spin_dif_rating, 1)
        layout_principal.addLayout(layout_configs)
        self.check_probabilidade = QCheckBox("🎲 Ativar Uniformização Probabilística (Balancear Elo e Aberturas)")
        layout_principal.addWidget(self.check_probabilidade)
        self.btn_rodar = QPushButton("🌊 Mergulhar nos Dados (Rodar Pipeline)")
        self.btn_rodar.clicked.connect(self.rodar_pipeline)
        self.btn_rodar.setEnabled(False) 
        layout_principal.addWidget(self.btn_rodar)
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
        dif_rating = self.spin_dif_rating.value()
        usar_prob = self.check_probabilidade.isChecked()
        self.btn_rodar.setEnabled(False)
        self.btn_arquivo.setEnabled(False)
        self.caixa_log.clear()
        self.thread = TrabalhadorPipeline(self.arquivo_selecionado, qtd, dif_rating, usar_prob)
        self.thread.sinal_concluido.connect(self.pipeline_finalizado)
        self.thread.start()
    def pipeline_finalizado(self):
        self.btn_rodar.setEnabled(True)
        self.btn_arquivo.setEnabled(True)

if __name__ == '__main__':
    mp.freeze_support() 
    app = QApplication(sys.argv)
    ex = SereiaApp()
    ex.show()
    sys.exit(app.exec_())