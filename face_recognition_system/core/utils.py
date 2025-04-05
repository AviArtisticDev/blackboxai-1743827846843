import cv2
import numpy as np
from gfpgan import GFPGANer
from basicsr.archs.rrdbnet_arch import RRDBNet
from realesrgan import RealESRGANer

class ImageEnhancer:
    def __init__(self):
        # Initialize GFPGAN for face restoration
        self.face_enhancer = GFPGANer(
            model_path='gfpgan/weights/GFPGANv1.4.pth',
            upscale=1,
            arch='clean',
            channel_multiplier=2,
            bg_upsampler=None
        )
        
        # Initialize RealESRGAN for general super-resolution
        self.sr_model = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64, num_block=23, num_grow_ch=32)
        self.upsampler = RealESRGANer(
            scale=4,
            model_path='realesrgan/weights/RealESRGAN_x4plus.pth',
            model=self.sr_model,
            tile=400
        )

    def enhance_image(self, image: np.ndarray) -> np.ndarray:
        """Apply enhancement pipeline to input image"""
        try:
            # Step 1: Low-light enhancement
            enhanced = self._enhance_low_light(image)
            
            # Step 2: Super-resolution
            enhanced = self._apply_super_resolution(enhanced)
            
            # Step 3: Face-specific enhancement
            enhanced = self._enhance_faces(enhanced)
            
            return enhanced
        except Exception as e:
            print(f"Enhancement failed: {e}")
            return image

    def _enhance_low_light(self, image: np.ndarray) -> np.ndarray:
        """Improve visibility in dark conditions"""
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
        limg = cv2.merge([clahe.apply(l), a, b])
        return cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)

    def _apply_super_resolution(self, image: np.ndarray) -> np.ndarray:
        """Increase resolution while preserving details"""
        sr_img, _ = self.upsampler.enhance(image, outscale=2)
        return sr_img

    def _enhance_faces(self, image: np.ndarray) -> np.ndarray:
        """Targeted enhancement for detected faces"""
        _, _, restored_faces = self.face_enhancer.enhance(
            image,
            has_aligned=False,
            only_center_face=False,
            paste_back=True
        )
        return restored_faces[0] if restored_faces else image

def enhance_image(image: np.ndarray) -> np.ndarray:
    """Global enhancement function (singleton pattern)"""
    if not hasattr(enhance_image, 'enhancer'):
        enhance_image.enhancer = ImageEnhancer()
    return enhance_image.enhancer.enhance_image(image)