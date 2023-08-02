import sys, os
import cv2
import json
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap, QImage, QIcon, QColor, QFont
from PyQt5.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget, QPushButton, QFileDialog, QMainWindow, QAction, QMenu, QScrollBar, QMessageBox

import numpy as np
from time import sleep
from openpose import list_mouvement
from openpose import config
from openpose.person import person
from openpose import person

MARGIN = config.MARGIN
ROW_SIZE = config.ROW_SIZE
FONT_SIZE = config.FONT_SIZE
FONT_THICKNESS = config.FONT_THICKNESS
TEXT_COLOR = config.TEXT_COLOR
FPS = config.FPS

sys.path.append('F:/openpose/build/python/openpose/Release');
os.environ['PATH']  = os.environ['PATH'] + ';' + 'F:/openpose/build/x64/Release;' +  'F:/openpose/build/bin;'
import pyopenpose as op

class VideoPlayer(QMainWindow):
    def __init__(self):
        super().__init__()

        # Création des variables pour le traitement des vidéos
        self.pause = False
        self.use_openpose = False
        self.list_person = None
        self.fps_wait = 40
        self.time_s = 0
        self.opWrapper = None
        self.datum = None

        # Création du label pour afficher les images de la vidéo
        self.label_video = QLabel(self)
        self.label_video.setAlignment(Qt.AlignCenter)

        # Création du bouton "Parcourir"
        self.button_browse = QPushButton("Parcourir")
        self.button_browse.clicked.connect(self.browse_video)

        # Create a QLabel widget for displaying "Les Fibres d'Ariann"
        self.label_title = QLabel("Les Fibres d'Ariann", self)
        self.label_title.setAlignment(Qt.AlignCenter)
        font = QFont("Arial", 36, QFont.Bold)
        self.label_title.setFont(font)
        self.label_title.setStyleSheet("color: black;")

        # Création de la barre de défilement
        self.scrollbar = QScrollBar(Qt.Horizontal)
        self.scrollbar.setStyleSheet(
        """
        QScrollBar:horizontal {
            background: transparent;
            height: 8px;
            margin: 0px;
            padding: 0px;
        }
        QScrollBar::handle:horizontal {
            background: #040404;
            border-radius: 10px;  /* Adjust the border radius to make it circular */
            height : 20px;
        }
        QScrollBar::handle:horizontal:hover {
            background: #a0a0a0;
        }
        QScrollBar::add-line:horizontal,
        QScrollBar::sub-line:horizontal {
            background: transparent;
            width: 0px;
            height: 0px;
        }
        QScrollBar::add-page:horizontal {
            background: gray;
        }
        QScrollBar::sub-page:horizontal {
            background: blue;
        }
        """
        )

        # Création de la mise en page verticale
        layout = QVBoxLayout()
        layout.addWidget(self.label_video)
        layout.addWidget(self.button_browse)
        layout.addWidget(self.scrollbar)

        central_widget = QWidget(self)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # Hide the scroll bar if no video is opened
        self.scrollbar.setVisible(False)

        central_widget = QWidget(self)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # Variables pour la vidéo
        self.video_path = ""
        self.video_capture = None
        self.timer = QTimer(self)
        if(self.use_openpose == False):
            self.timer.timeout.connect(self.update_video)
        else :
            self.timer.timeout.connect(self.update_video_openpose)

        # Création du menu "Fichier"
        file_menu = self.menuBar().addMenu("Fichier")

        # Création de l'action "Ouvrir"
        open_action = QAction("Ouvrir", self)
        open_action.triggered.connect(self.browse_video)
        file_menu.addAction(open_action)

        # Création du sous-menu "Ouvrir récent"
        self.recent_files_menu = QMenu("Ouvrir récent", self)
        file_menu.addMenu(self.recent_files_menu)

        # Création de l'action "Fermer"
        self.exit_action = QAction("Fermer", self)
        self.exit_action.triggered.connect(self.exit_video)
        self.exit_action.setEnabled(False)  # Initially disable the action
        file_menu.addAction(self.exit_action)

        # Charger les fichiers récents
        self.load_recent_files()
        self.update_recent_files_menu()

        # Définir la taille de la fenêtre
        self.resize(1600, 900)  # Remplacez par la taille souhaitée

        # Création de l'action "Quitter"
        exit_action = QAction("Quitter", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Création du menu "Affichage"
        Display_menu = self.menuBar().addMenu("Affichage")

        # Création de l'action "Openpose"
        openpose_action = QAction("Openpose",self)
        openpose_action.triggered.connect(self.setup_openpose)
        Display_menu.addAction(openpose_action)

        # Création du menu "Lecteur"
        lec_menu = self.menuBar().addMenu("Lecteur")

        # Création de l'action "Lecture"
        run_action = QAction("Lecture",self)
        run_action.triggered.connect(self.run)
        lec_menu.addAction(run_action)

        # Création de l'action "Pause"
        pause_action = QAction("Pause",self)
        pause_action.triggered.connect(self.stop)
        lec_menu.addAction(pause_action)

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
        print("Ouverture de la vidéo")
        self.timer.start(30)  # Set the video display update frequency

        # Retrieve the total duration of the video
        total_frames = int(self.video_capture.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = int(self.video_capture.get(cv2.CAP_PROP_FPS))
        total_duration = total_frames / fps * 1000  # Duration in milliseconds

        self.scrollbar.setMinimum(0)
        self.scrollbar.setMaximum(int(total_duration))

        # Hide the "Parcourir" push button
        self.button_browse.setVisible(False)

        # Show the scroll bar if a video is opened
        self.scrollbar.setVisible(True)

        # Enable the "Fermer" button if a video is opened
        self.exit_action.setEnabled(True)

    def run(self):
        self.pause = False

    def stop(self):
        self.pause = True

    def update_video(self):
        if not self.pause :
            ret, frame = self.video_capture.read()
            if ret:
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    image = QImage(frame_rgb.data, frame_rgb.shape[1], frame_rgb.shape[0], QImage.Format_RGB888)
                    pixmap = QPixmap.fromImage(image)
                    self.label_video.setPixmap(pixmap.scaled(self.label_video.size(), Qt.AspectRatioMode.KeepAspectRatio))

                    # Get the current position in milliseconds
                    current_position = int(self.video_capture.get(cv2.CAP_PROP_POS_MSEC))

                    # Set the scrollbar value
                    self.scrollbar.setValue(int(current_position))
            else:
                self.timer.stop()
                self.video_capture.release()

    def update_video_openpose(self) :
        if not self.pause : 
            ret, frame = self.video_capture.read()
            if ret : 
                self.time_s += 1/FPS
            
                self.list_person.fill(None)
                self.datum.cvInputData = frame
                self.opWrapper.emplaceAndPop([self.datum])

                poseKeypoints = self.datum.poseKeypoints

                if poseKeypoints.size > 1:
                    for keypoints in poseKeypoints:
                        person.person.tracking(keypoints, self.list_person)

                for p in self.list_person :
                    p.update()

                frame = person.Show_list_person(frame, self.list_person)

            else :
                self.timer.stop()
                self.video_capture.release()

    def exit_video(self):
        if self.video_capture and self.video_capture.isOpened():
            # Create a QMessageBox to ask the user whether to save the video
            message_box = QMessageBox(self)
            message_box.setWindowTitle("Enregistrer la vidéo")
            message_box.setText("Enregistrer les données dans un fichier ?")
            message_box.setIcon(QMessageBox.Question)
            message_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            message_box.setDefaultButton(QMessageBox.Yes)

            # Connect the buttons to the appropriate actions
            yes_button = message_box.button(QMessageBox.Yes)
            yes_button.clicked.connect(self.save_and_exit)
            no_button = message_box.button(QMessageBox.No)
            no_button.clicked.connect(self.close_video)

            message_box.exec_()
        else:
            self.close_video()

    def save_and_exit(self):
        # Code pour enregistrer les données openpose actuelles
        print("Enregistrement des donnees")
        self.close_video()

    def close_video(self):
        self.timer.stop()
        self.video_capture.release()
        self.scrollbar.setVisible(False)
        self.button_browse.setVisible(True)
        
        # Reset the state of the label_video widget
        self.label_video.clear()
        self.label_video.update()

        # Disable the "Fermer" button if no video is opened
        self.exit_action.setEnabled(False)

    def setup_openpose(self): 
        self.fps_wait        = 10
        self.time_s          = 0
        self.list_person = np.empty([100, 5], dtype=person.person)

        self.opWrapper = op.WrapperPython()
        self.opWrapper.configure(dict(model_folder="F:/openpose/models/"))
        self.opWrapper.start()
        self.datum = op.Datum()

        self.use_openpose == True

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
        file_path = ".recent_files.json"
        if not os.path.exists(file_path):
            with open(file_path, "w") as file:
                json.dump([], file)

        with open(file_path, "r") as file:
            recent_files = json.load(file)
        return recent_files

    def save_recent_files(self, recent_files):
        with open(".recent_files.json", "w") as file:
            json.dump(recent_files, file)

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Création de la fenêtre de l'application
    window = VideoPlayer()
    window.setWindowTitle("Lecteur vidéo")
    window.show()

    sys.exit(app.exec_())
