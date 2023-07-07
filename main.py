import sys, os
import cv2
import json
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget, QPushButton, QFileDialog, QMainWindow, QAction, QMenu

class VideoPlayer(QMainWindow):
    def __init__(self):
        super().__init__()

        # Création du label pour afficher les images de la vidéo
        self.label_video = QLabel(self)
        self.label_video.setAlignment(Qt.AlignCenter)

        # Création du bouton "Parcourir"
        self.button_browse = QPushButton("Parcourir")
        self.button_browse.clicked.connect(self.browse_video)

        # Création de la mise en page verticale
        layout = QVBoxLayout()
        layout.addWidget(self.label_video)
        layout.addWidget(self.button_browse)

        central_widget = QWidget(self)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # Variables pour la vidéo
        self.video_path = ""
        self.video_capture = None
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_video)

        # Création du menu "Fichier"
        file_menu = self.menuBar().addMenu("Fichier")

        # Création de l'action "Ouvrir"
        open_action = QAction("Ouvrir", self)
        open_action.triggered.connect(self.browse_video)
        file_menu.addAction(open_action)

        # Création du sous-menu "Ouvrir récent"
        self.recent_files_menu = QMenu("Ouvrir récent", self)
        file_menu.addMenu(self.recent_files_menu)

        # Charger les fichiers récents
        self.load_recent_files()

        # Définir la taille de la fenêtre
        self.resize(1600, 900)  # Remplacez par la taille souhaitée

        # Création de l'action "Quitter"
        exit_action = QAction("Quitter", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

    def browse_video(self):
        file_dialog = QFileDialog()
        video_file, _ = file_dialog.getOpenFileName(self, "Sélectionner une vidéo", "",
                                                    "Fichiers vidéo (*.mp4 *.avi *.mkv)")
        if video_file:
            self.video_path = video_file
            self.start_video()

            # Ajouter le fichier ouvert récemment
            self.add_recent_file(video_file)

    def start_video(self):
        self.video_capture = cv2.VideoCapture(self.video_path)
        self.timer.start(30)  # Définit la fréquence de mise à jour de l'affichage de la vidéo

    def update_video(self):
        ret, frame = self.video_capture.read()
        if ret:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image = QImage(frame_rgb.data, frame_rgb.shape[1], frame_rgb.shape[0], QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(image)
            self.label_video.setPixmap(pixmap.scaled(self.label_video.size(), Qt.AspectRatioMode.KeepAspectRatio))
        else:
            self.timer.stop()
            self.video_capture.release()

    def add_recent_file(self, file_path):
        # Charger les fichiers récents existants
        recent_files = self.load_recent_files()

        # Ajouter le fichier à la liste des fichiers récents
        if file_path in recent_files:
            recent_files.remove(file_path)
        recent_files.insert(0, file_path)

        # Limiter la liste à 5 éléments maximum
        recent_files = recent_files[:5]

        # Enregistrer la liste des fichiers récents
        self.save_recent_files(recent_files)

        # Mettre à jour le menu "Ouvrir récent"
        self.update_recent_files_menu()

    def update_recent_files_menu(self):
        self.recent_files_menu.clear()

        # Charger la liste des fichiers récents
        recent_files = self.load_recent_files()

        for file_path in recent_files:
            action = QAction(file_path, self)
            action.triggered.connect(lambda _, path=file_path: self.open_recent_file(path))
            self.recent_files_menu.addAction(action)

    def open_recent_file(self, file_path):
        self.video_path = file_path
        self.start_video()

    def load_recent_files(self):
        file_path = "recent_files.json"
        if not os.path.exists(file_path):
            with open(file_path, "w") as file:
                json.dump([], file)

        with open(file_path, "r") as file:
            recent_files = json.load(file)
        return recent_files

    def save_recent_files(self, recent_files):
        with open("recent_files.json", "w") as file:
            json.dump(recent_files, file)

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Création de la fenêtre de l'application
    window = VideoPlayer()
    window.update_recent_files_menu()
    window.setWindowTitle("Lecteur vidéo")
    window.show()

    sys.exit(app.exec_())
