from flask import Flask, render_template, Response, request, redirect, url_for
import cv2
import numpy as np
import logging
import threading

app = Flask(__name__)

logging.basicConfig(filename='parking_log.txt', level=logging.INFO, format='%(asctime)s - %(message)s')

vagas_estacionamentos2 = [
    [563, 381, 95, 203],
    [429, 362, 116, 219],
    [312, 358, 112, 212],
    [192, 348, 110, 216],
    [676, 374, 121, 229],
    [796, 383, 126, 228],
    [922, 392, 135, 225],
    [1072, 404, 112, 219]
]

vagas_estacionamentos = [
    [1, 89, 108, 213],
    [115, 87, 152, 211],
    [289, 89, 138, 212],
    [439, 87, 135, 212],
    [591, 90, 132, 206],
    [738, 93, 139, 204],
    [881, 93, 138, 201],
    [1027, 94, 147, 202]
]

estacionamentos = [
    {'video': 'static/video.mp4', 'vagas': vagas_estacionamentos},
    {'video': 'static/video2.mp4', 'vagas': vagas_estacionamentos2},
]

# Flags para controle do processamento dos vídeos
process_video_flags = [False] * len(estacionamentos)
webcam_flag = False

def process_video(index):
    global process_video_flags
    vagas = estacionamentos[index]['vagas']
    video_path = estacionamentos[index]['video']
    estado_anterior = [0] * len(vagas)

    while process_video_flags[index]:
        video = cv2.VideoCapture(video_path)
        if not video.isOpened():
            logging.error(f"Erro ao abrir o vídeo: {video_path}")
            return

        logging.info(f"Iniciando processamento do vídeo: {video_path}")

        while process_video_flags[index]:
            ret, img = video.read()
            if not ret:
                logging.info(f"Fim do vídeo: {video_path}")
                break

            imgCinza = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            imgTh = cv2.adaptiveThreshold(imgCinza, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 25, 16)
            imgBlur = cv2.medianBlur(imgTh, 5)
            kernel = np.ones((3, 3), np.int8)
            imgDil = cv2.dilate(imgBlur, kernel)

            qtVagasAbertas = 0
            for i, (x, y, w, h) in enumerate(vagas):
                recorte = imgDil[y:y+h, x:x+w]
                qtPxBranco = cv2.countNonZero(recorte)
                cv2.putText(img, str(qtPxBranco), (x, y+h-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

                if qtPxBranco > 3000 and estado_anterior[i] == 0:
                    logging.info(f'Estacionamento {index+1} - Vaga {i+1} preenchida.')
                    estado_anterior[i] = 1
                elif qtPxBranco <= 3000 and estado_anterior[i] == 1:
                    logging.info(f'Estacionamento {index+1} - Vaga {i+1} liberada.')
                    estado_anterior[i] = 0

                if qtPxBranco <= 3000:
                    cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 3)
                    qtVagasAbertas += 1
                else:
                    cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 3)

            cv2.rectangle(img, (90, 0), (300, 60), (255, 0, 0), -1)
            cv2.putText(img, f'LIVRE: {qtVagasAbertas}/{len(vagas)}', (95, 45), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 5)

            ret, jpeg = cv2.imencode('.jpg', img)
            frame = jpeg.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
        video.release()

def process_webcam():
    global webcam_flag
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        logging.error("Erro ao abrir a webcam")
        return

    logging.info("Iniciando processamento da webcam")

    while webcam_flag:
        ret, img = cap.read()
        if not ret:
            logging.info("Erro ao capturar imagem da webcam")
            break

        imgCinza = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        imgTh = cv2.adaptiveThreshold(imgCinza, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 25, 16)
        imgBlur = cv2.medianBlur(imgTh, 5)
        kernel = np.ones((3, 3), np.int8)
        imgDil = cv2.dilate(imgBlur, kernel)

        ret, jpeg = cv2.imencode('.jpg', img)
        frame = jpeg.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

    cap.release()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Aqui você pode adicionar a lógica de autenticação
        return redirect(url_for('menu'))
    return render_template('login.html')

@app.route('/menu')
def menu():
    return render_template('menu.html')

@app.route('/start/<int:index>', methods=['POST'])
def start(index):
    global process_video_flags
    process_video_flags[index] = True
    threading.Thread(target=process_video, args=(index,)).start()
    logging.info(f'Processo {index+1} iniciado')
    return f'Processo {index+1} iniciado'

@app.route('/stop/<int:index>', methods=['POST'])
def stop(index):
    global process_video_flags
    process_video_flags[index] = False
    logging.info(f'Processo {index+1} parado')
    return f'Processo {index+1} parado'

@app.route('/video_feed/<int:index>')
def video_feed(index):
    return Response(process_video(index), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/webcam_feed')
def webcam_feed():
    global webcam_flag
    webcam_flag = True
    threading.Thread(target=process_webcam).start()
    return Response(process_webcam(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/stop_webcam', methods=['POST'])
def stop_webcam():
    global webcam_flag
    webcam_flag = False
    logging.info('Webcam parada')
    return 'Webcam parada'

if __name__ == '__main__':
    app.run(debug=True)
