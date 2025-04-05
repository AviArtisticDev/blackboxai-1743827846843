import cv2
import numpy as np
import logging
from typing import Optional
from deep_sort_realtime.deepsort_tracker import DeepSort
from insightface.app import FaceAnalysis
from .utils import enhance_image

class FaceProcessor:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.tracker = DeepSort(max_age=30)
        
        # Initialize face analysis with detection+recognition models
        self.face_app = FaceAnalysis(
            name='buffalo_l',
            providers=['CUDAExecutionProvider', 'CPUExecutionProvider']
        )
        self.face_app.prepare(ctx_id=0, det_size=(640, 640))
        
        self.running = False
        self.current_frame = None
        self.detections = []

    def start(self, video_source: Optional[str] = None):
        """Start processing video stream"""
        self.running = True
        cap = cv2.VideoCapture(video_source or 0)
        
        try:
            while self.running:
                ret, frame = cap.read()
                if not ret:
                    break
                    
                self.current_frame = frame
                self._process_frame()
                
        finally:
            cap.release()
            self.cleanup()

    def _process_frame(self):
        """Process a single frame for face detection and recognition"""
        # Step 1: Image enhancement for low-light/blurry conditions
        enhanced_frame = enhance_image(self.current_frame)
        
        # Step 2: Face detection
        faces = self.face_app.get(enhanced_frame)
        
        # Step 3: Tracking with DeepSORT
        tracks = self.tracker.update_tracks(
            self._prepare_detections(faces), 
            frame=enhanced_frame
        )
        
        # Step 4: Recognition and alert logic
        self._process_tracks(tracks, faces)

    def _prepare_detections(self, faces):
        """Convert face detections to DeepSORT format"""
        detections = []
        for face in faces:
            bbox = face.bbox.astype(int)
            detections.append([
                bbox[0], bbox[1], bbox[2]-bbox[0], bbox[3]-bbox[1],  # x,y,w,h
                face.det_score  # confidence
            ])
        return detections

    def _process_tracks(self, tracks, faces):
        """Match tracks with recognized faces and trigger alerts"""
        # TODO: Implement database matching and alert logic
        pass

    def cleanup(self):
        """Release resources"""
        self.running = False
        self.tracker = None
        self.face_app = None