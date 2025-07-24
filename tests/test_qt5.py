#!/usr/bin/env python3
# Script de prueba para verificar PyQt5

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget

class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Test PyQt5")
        self.setGeometry(100, 100, 400, 300)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        label = QLabel("¡PyQt5 funciona correctamente!")
        button = QPushButton("Cerrar")
        button.clicked.connect(self.close)
        
        layout.addWidget(label)
        layout.addWidget(button)

def main():
    print("Iniciando test de PyQt5...")
    app = QApplication(sys.argv)
    print("QApplication creada")
    
    window = TestWindow()
    print("Ventana creada")
    
    window.show()
    print("Ventana mostrada")
    
    print("Iniciando loop de eventos...")
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
