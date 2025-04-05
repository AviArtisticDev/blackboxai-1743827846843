from flask import Flask, jsonify, Response
from flask_socketio import SocketIO
from flask_cors import CORS
import logging
import cv2
import numpy as np
from threading import Lock
from core.face_processor import FaceProcessor
from alerts.notification_service import send_alert

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")
thread = None
thread_lock = Lock()
processor = None

@app.route('/api/status')
def status():
    return jsonify({
        'status': 'running',
        'detections': processor.detections if processor else []
    })

@app.route('/api/start', methods=['POST'])
def start_processing():
    global processor
    with thread_lock:
        if processor is None or not processor.running:
            processor = FaceProcessor()
            socketio.start_background_task(processor.start)
            return jsonify({'status': 'started'})
    return jsonify({'status': 'already running'})

@app.route('/api/stop', methods=['POST'])
def stop_processing():
    global processor
    with thread_lock:
        if processor and processor.running:
            processor.cleanup()
            processor = None
            return jsonify({'status': 'stopped'})
    return jsonify({'status': 'not running'})

def generate_frames():
    while True:
        with thread_lock:
            if processor and processor.current_frame is not None:
                frame = processor.current_frame
                ret, buffer = cv2.imencode('.jpg', frame)
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                   mimetype='multipart/x-mixed-replace; boundary=frame')

def start_server():
    """Start the web server"""
    logging.info("Starting web server on http://localhost:8000")
    socketio.run(app, host='0.0.0.0', port=8000, debug=False)