import sys
import os
import csv
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QLineEdit,
    QLabel, QRadioButton, QHBoxLayout, QTextEdit, QTableWidget,
    QTableWidgetItem, QFileDialog, QStackedWidget, QMessageBox
)
from PyQt5.QtPrintSupport import QPrintDialog, QPrinter
from PyQt5.QtGui import QTextDocument
from PyQt5.QtCore import Qt

class SoruBankasiApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Soru Bankası Uygulaması")
        self.sorular = []
        self.csv_path = os.path.join(os.getcwd(), "soru_bankasi.csv")
        self.init_ui()
        if os.path.exists(self.csv_path):
            self.csvden_sorulari_yukle(self.csv_path)

    def init_ui(self):
        self.layout = QVBoxLayout(self)
        self.stack = QStackedWidget(self)

        # Giriş sayfası
        giris = QWidget()
        gl = QVBoxLayout(giris)
        gl.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        title = QLabel("Soru Bankası Uygulaması")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 24px; font-weight: bold; text-align: center")
        gl.addWidget(title)

        btn_yeni = QPushButton("Yeni Soru Ekle")
        btn_yeni.setStyleSheet("QPushButton {text-align: center;}")
        btn_sec = QPushButton("Soru Seç")
        for btn in (btn_yeni, btn_sec):
            btn.setFixedHeight(40)
            btn.setFixedWidth(200)
        btn_yeni.clicked.connect(lambda: self.stack.setCurrentWidget(self.yeni_widget))
        btn_sec.clicked.connect(lambda: self.stack.setCurrentWidget(self.sec_widget))
        gl.addSpacing(20)
        gl.addWidget(btn_yeni)
        gl.addWidget(btn_sec)
        self.stack.addWidget(giris)

        # Yeni soru sayfası
        self.yeni_widget = QWidget()
        yl = QVBoxLayout(self.yeni_widget)
        self.edit_soru = QTextEdit()
        self.edit_soru.setPlaceholderText("Soru metnini giriniz")
        yl.addWidget(QLabel("Soru:"))
        yl.addWidget(self.edit_soru)
        self.secenek_edits = []
        for i in range(5):
            hl = QHBoxLayout()
            rd = QRadioButton(chr(65+i))
            ed = QLineEdit()
            ed.setPlaceholderText(f"Şık {chr(65+i)}")
            hl.addWidget(rd)
            hl.addWidget(ed)
            yl.addLayout(hl)
            self.secenek_edits.append(ed)
        btn_ekle = QPushButton("Bankaya Ekle")
        btn_ekle.setFixedHeight(30)
        btn_ekle.clicked.connect(self.soru_ekle)
        yl.addWidget(btn_ekle)
        self.tablo = QTableWidget(0,6)
        self.tablo.setHorizontalHeaderLabels(["Soru","A","B","C","D","E"])
        yl.addWidget(self.tablo)
        btn_kaydet = QPushButton("CSV Kaydet")
        btn_kaydet.setFixedHeight(30)
        btn_kaydet.clicked.connect(self.csvye_kaydet)
        yl.addWidget(btn_kaydet)
        self.stack.addWidget(self.yeni_widget)

        # Soru seçme sayfası
        self.sec_widget = QWidget()
        sl = QVBoxLayout(self.sec_widget)
        self.sec_table = QTableWidget()
        sl.addWidget(self.sec_table)
        btn_dosya = QPushButton("CSV Dosya Seç")
        btn_dosya.setFixedHeight(30)
        btn_dosya.clicked.connect(self.dosya_sec)
        sl.addWidget(btn_dosya)
        btn_yazdir = QPushButton("Yazdır")
        btn_yazdir.setFixedHeight(30)
        btn_yazdir.clicked.connect(self.yazdir)
        sl.addWidget(btn_yazdir)
        self.stack.addWidget(self.sec_widget)

        self.layout.addWidget(self.stack)

    def soru_ekle(self):
        metin = self.edit_soru.toPlainText().strip()
        secenekler = [ed.text().strip() for ed in self.secenek_edits]
        if not metin or not all(secenekler):
            QMessageBox.warning(self, "Hata", "Lütfen tüm alanları doldurunuz.")
            return
        kayit = [metin] + secenekler
        self.sorular.append(kayit)
        self._tablo_satir(self.tablo, kayit)

    def _tablo_satir(self, tablo, kayit):
        r = tablo.rowCount()
        tablo.insertRow(r)
        for c, val in enumerate(kayit):
            tablo.setItem(r, c, QTableWidgetItem(val))

    def csvye_kaydet(self):
        if not self.sorular:
            QMessageBox.warning(self, "Hata", "Kaydedilecek soru yok.")
            return
        path, _ = QFileDialog.getSaveFileName(self, "CSV Kaydet", "soru_bankasi.csv", "CSV Files (*.csv)")
        if path:
            with open(path, 'w', newline='', encoding='utf-8') as f:
                w = csv.writer(f)
                w.writerow(["Soru","A","B","C","D","E"])
                w.writerows(self.sorular)
            QMessageBox.information(self, "Başarılı", "CSV olarak kaydedildi.")

    def csvden_sorulari_yukle(self, yol):
        try:
            with open(yol, newline='', encoding='utf-8') as f:
                r = csv.reader(f)
                next(r, None)
                self.sorular = [row for row in r]
            self.tablo.setRowCount(0)
            for kayit in self.sorular:
                self._tablo_satir(self.tablo, kayit)
        except Exception as e:
            QMessageBox.warning(self, "Hata", f"Dosya okunamadı: {e}")

    def dosya_sec(self):
        path, _ = QFileDialog.getOpenFileName(self, "CSV Dosyası Seç", "", "CSV Files (*.csv)")
        if path:
            self.csvden_sorulari_yukle(path)
            self.sec_table.setColumnCount(6)
            self.sec_table.setHorizontalHeaderLabels(["Soru","A","B","C","D","E"])
            self.sec_table.setRowCount(0)
            for kayit in self.sorular:
                self._tablo_satir(self.sec_table, kayit)
        else:
            QMessageBox.warning(self, "Uyarı", "Dosya seçilmedi.")

    def yazdir(self):
        if not self.sorular:
            QMessageBox.warning(self, "Uyarı", "Önce dosya seçiniz.")
            return
        printer = QPrinter(QPrinter.HighResolution)
        dlg = QPrintDialog(printer, self)
        if dlg.exec_() == QPrintDialog.Accepted:
            doc = QTextDocument()
            html = '<h2>Soru Bankası</h2><table border="1" cellpadding="4">'
            html += '<tr>' + ''.join(f'<th>{h}</th>' for h in ["Soru","A","B","C","D","E"]) + '</tr>'
            for kayit in self.sorular:
                html += '<tr>' + ''.join(f'<td>{v}</td>' for v in kayit) + '</tr>'
            html += '</table>'
            doc.setHtml(html)
            doc.print_(printer)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = SoruBankasiApp()
    w.resize(800, 600)
    w.show()
    sys.exit(app.exec_())