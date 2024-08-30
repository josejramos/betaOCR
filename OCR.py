import cv2
import pandas as pd
from ultralytics import YOLO
import numpy as np
import easyocr
from datetime import datetime
import tkinter as tk
from tkinter import Frame
from PIL import Image, ImageTk
import threading

# Inicializa o leitor EasyOCR
reader = easyocr.Reader(['en'])

# Carrega o modelo YOLOv8 pré-treinado
model = YOLO('modelo/best.pt')

# Lista de classes para YOLO
with open("coco1.txt", "r") as my_file:
    class_list = my_file.read().split("\n")

# Área de análise original
original_width, original_height = 1020, 510
analysis_ratio = 0.35
analysis_width = int(original_width * analysis_ratio)
analysis_height = int(original_height * analysis_ratio)

def calculate_dimensions(area):
    width = area[2][0] - area[0][0]
    height = area[1][1] - area[0][1]
    return width, height

def get_analysis_area_coords(width, height, analysis_width, analysis_height):
    x_min_area = (width - analysis_width) // 2
    y_min_area = (height - analysis_height) // 2
    x_max_area = x_min_area + analysis_width
    y_max_area = y_min_area + analysis_height
    return x_min_area, y_min_area, x_max_area, y_max_area

def resize_analysis_area(original_width, original_height, target_width, target_height):
    aspect_ratio = original_width / original_height
    new_height = target_height
    new_width = int(new_height * aspect_ratio)
    if new_width > target_width:
        new_width = target_width
        new_height = int(new_width / aspect_ratio)
    
    width_scale = new_width / original_width
    height_scale = new_height / original_height

    scaled_width = int(analysis_width * width_scale)
    scaled_height = int(analysis_height * height_scale)

    return get_analysis_area_coords(new_width, new_height, scaled_width, scaled_height)

class CameraApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Monitoramento de Câmeras")
        self.root.geometry("1200x800")  # Ajustado para 4 câmeras
        
        self.rtsp_links = [
            'resources/mycarplate.mp4',#adicione as câmeras 
        ]
        
        self.frames = [None] * len(self.rtsp_links)
        self.canvas = [None] * len(self.rtsp_links)
        self.video_sources = [None] * len(self.rtsp_links)
        self.processed_numbers = set()  # Inicializando o conjunto de placas processadas
        
        # Criar o layout da interface
        self.create_widgets()
        
        # Iniciar captura de vídeo
        self.start_video_stream()

    def create_widgets(self):
        for i in range(len(self.rtsp_links)):
            frame = Frame(self.root, width=600, height=360)
            frame.grid(row=i // 2, column=i % 2, padx=10, pady=10)
            self.canvas[i] = tk.Canvas(frame, width=600, height=360)
            self.canvas[i].pack()

    def analyze_frame(self, frame):
        height, width = frame.shape[:2]
        x_min_area, y_min_area, x_max_area, y_max_area = resize_analysis_area(original_width, original_height, width, height)
        
        results = model.predict(frame)
        a = results[0].boxes.data
        px = pd.DataFrame(a).astype("float")
   
        for index, row in px.iterrows():
            x1, y1, x2, y2, _, d = map(int, row)
            c = class_list[d]
            cx = int(x1 + x2) // 2
            cy = int(y1 + y2) // 2
            if x_min_area <= cx <= x_max_area and y_min_area <= cy <= y_max_area:
                crop = frame[y1:y2, x1:x2]
                text = reader.readtext(crop, detail=0, paragraph=False)
                if text:
                    text = text[0].replace('(', '').replace(')', '').replace(',', '').replace(']', '')
                    if text and text not in self.processed_numbers:
                        self.processed_numbers.add(text)
                        self.log_plate(text)
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 1)
                        cv2.imshow('crop', crop)
      
        cv2.rectangle(frame, (x_min_area, y_min_area), (x_max_area, y_max_area), (255, 0, 0), 2)
        return frame

    def log_plate(self, text):
        with open("car_plate_data.txt", "a") as file:
            current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            file.write(f"{text}\t{current_datetime}\n")

    def update_frame(self, index):
        while True:
            ret, frame = self.video_sources[index].read()
            if not ret:
                break
            if index == 0:  # Analisar apenas o feed da primeira câmera
                frame = self.analyze_frame(frame)
            # Redimensionar frame para manter proporções 600x360
            height, width = frame.shape[:2]
            aspect_ratio = width / height
            new_height = 360
            new_width = int(new_height * aspect_ratio)
            if new_width > 600:
                new_width = 600
                new_height = int(new_width / aspect_ratio)
            resized_frame = cv2.resize(frame, (new_width, new_height))
            padding_frame = np.zeros((360, 600, 3), dtype=np.uint8)
            padding_frame[:new_height, :new_width] = resized_frame
            frame = cv2.cvtColor(padding_frame, cv2.COLOR_BGR2RGB)
            image = Image.fromarray(frame)
            photo = ImageTk.PhotoImage(image=image)
            def update_canvas():
                self.canvas[index].create_image(0, 0, image=photo, anchor=tk.NW)
                self.canvas[index].image = photo
            self.root.after(0, update_canvas)
            cv2.waitKey(1)

    def start_video_stream(self):
        for i in range(len(self.rtsp_links)):
            self.video_sources[i] = cv2.VideoCapture(self.rtsp_links[i])
            thread = threading.Thread(target=self.update_frame, args=(i,))
            thread.daemon = True
            thread.start()

if __name__ == "__main__":
    root = tk.Tk()
    app = CameraApp(root)
    root.mainloop()
