from dataclasses import dataclass
import logging
from pathlib import Path
import pickle
import time
from typing import cast
import numpy as np
from datetime import datetime
from PIL import Image
from PySide6.QtCore import Slot, Signal, QObject, QThread, QRunnable, QThreadPool, QBuffer
from PySide6.QtGui import QImage, QVector3D, QQuaternion, QMatrix3x3
from PySide6.QtWidgets import QApplication

import mediapipe as mp # type: ignore
from mediapipe.tasks import python # type: ignore
from mediapipe.tasks.python import vision # type: ignore
from mediapipe.tasks.python.vision.core import vision_task_running_mode  # type: ignore
from common.dtos.head_data import HeadProps # type: ignore

from common.services.video.types import VideoService

from .face_geometry import PCF, get_metric_landmarks_of_refined
from PIL import Image
import sys

from transforms3d.axangles import axangle2mat # type: ignore

logging.getLogger('PIL').setLevel(logging.WARNING)


def qimage_to_pil_image(qimage:QImage):
    """Convert QImage to PIL Image."""
    format = qimage.format()
    # QImage.Format_RGB32 means the image is stored using a 32-bit RGB format (0xffRRGGBB).
    if not(format == QImage.Format.Format_RGB32 or format == QImage.Format.Format_ARGB32):
        qimage = qimage.convertToFormat(QImage.Format.Format_ARGB32)
    buffer = qimage.bits()#.asarray(qimage.sizeInBytes())
    pil_image = Image.frombytes("RGBA", (qimage.width(), qimage.height()), buffer)
    return pil_image

def pil_image2mp_image(pil_image:Image.Image):
    return mp.Image(mp.ImageFormat.SRGB, np.array(pil_image.convert('RGB')))


@dataclass(frozen=True)
class FaceScanResult:
    timestamp:datetime
    head_visible:bool
    head_props:HeadProps|None


class _ScannerSignals(QObject):
    face_scanned = Signal(FaceScanResult)
    started = Signal()
    finished = Signal()


class _Scanner(QRunnable):
    def __init__(self) -> None:
        super().__init__()
        self.signals = _ScannerSignals()
        self._current_frame:VideoService.TimestampedFrame|None = None
        self._pcf:PCF|None = None
        self.detector:vision.FaceLandmarker = None
        self.first_detection_in_sequence = True
        self.smoothed_rotation_quat = QQuaternion()
        self.smoothed_translation = QVector3D()

    def initialize_at_first_image(self, image:QImage):
        self._pcf = PCF(image.width(),image.height())
        run_video_mode = vision_task_running_mode.VisionTaskRunningMode.VIDEO
        
        base_options = python.BaseOptions(model_asset_path=str(Path(__file__).parent / 'face_landmarker.task'))
        options = vision.FaceLandmarkerOptions(base_options=base_options,
                                            output_face_blendshapes=False,
                                            output_facial_transformation_matrixes=True,
                                            num_faces=1, running_mode=run_video_mode)
        
        self.detector = vision.FaceLandmarker.create_from_options(options)

    def is_running(self):
        return self._running

    @Slot()
    def run(self):
        self.signals.started.emit()
        start_timestamp =  datetime.now()
        last_frame_mcs = 0
        self._running = True
        try:
            while self._running:
                # time.sleep(0.1)
                # print('_Scanner.run time =', time.time())
                # return
                timestamp = datetime.now()
                timestamp_mcs = int((timestamp - start_timestamp).total_seconds()*1000)
                timestamp_mcs = max(timestamp_mcs, last_frame_mcs+1)

                if (frame:=self._current_frame) is not None:
                    self._current_frame = None
                    qimage = frame.frame.toImage()

                    
                    if self._pcf is None:
                        self.initialize_at_first_image(qimage)
                        start_timestamp = datetime.now()

                    timestamp = frame.timestamp
                    timestamp_mcs = int((timestamp - start_timestamp).total_seconds()*1000)
                    timestamp_mcs = max(timestamp_mcs, last_frame_mcs+1)

                    
                    # continue
                    time_start_scan = time.time()
                    scan_res = self._do_scan(qimage, timestamp, timestamp_mcs)
                    # print('time scan', time.time() - time_start_scan)
                    # if scan_res.head_props:
                    #     print(f'{scan_res.head_props.translation}')
                    self.signals.face_scanned.emit(scan_res)
                    
                last_frame_mcs = timestamp_mcs
                time.sleep(0.01)
        except Exception as e:
            import traceback
            print('Exception in _Scanner', e, traceback.format_exc())
            
        finally:
            print('finished')
            self.signals.finished.emit()

    def _do_scan(self, qimage:QImage, raw_timestamp, timestamp_mcs:int):
        # print('before Image.fromqimage')
        start_time = time.time()
        pil_img = qimage_to_pil_image(qimage)
        # print('after Image.fromqimage')
        mp_image = pil_image2mp_image(pil_img)
        # print('convert images time', time.time() - start_time)

        self.detection_result = self.detector.detect_for_video(mp_image, timestamp_mcs)
        
        if self.detection_result.face_landmarks:
            
            self.raw_landmarks = self.detection_result.face_landmarks[0]
            landmarks = np.array([(lm.x,lm.y,lm.z) for lm in self.raw_landmarks])
            
            landmarks = landmarks.T

            landmarks_head_space, _, head2cam_transform_mat = get_metric_landmarks_of_refined(landmarks, cast(PCF, self._pcf))
            head2cam_transform_mat = cast(np.ndarray, self.detection_result.facial_transformation_matrixes[0])
            landmarks_head_space = landmarks_head_space / 100

            head2cam_transform_mat = head2cam_transform_mat
            head2cam_transform_mat[:3, 3] /= 100

            rotate_opposite_direction_quat = QQuaternion.fromAxisAndAngle(QVector3D(0, 1, 0), 180)
            rotation_mat = head2cam_transform_mat[:3, :3]
            rotation_quat = QQuaternion.fromRotationMatrix(QMatrix3x3(rotation_mat.flatten().tolist())) * rotate_opposite_direction_quat
            translation = QVector3D(*head2cam_transform_mat[:-1,-1])
            m = np.array(rotate_opposite_direction_quat.toRotationMatrix().data()).reshape(3, 3)
            landmarks_head_space  = m @ landmarks_head_space

            if self.first_detection_in_sequence:
                self.smoothed_rotation_quat = rotation_quat
                self.smoothed_translation = translation
            else:
                self.smoothed_rotation_quat = QQuaternion.slerp(self.smoothed_rotation_quat, rotation_quat, 0.8)
                self.smoothed_translation = self.smoothed_translation * 0.8 + translation * 0.2
            
            head_props = HeadProps(self.smoothed_translation,
                                    self.smoothed_rotation_quat,
                                    landmarks_head_space.T)
            self.last_scan_result = FaceScanResult(raw_timestamp, True, head_props)
            
            self.first_detection_in_sequence = False
        else:
            self.last_scan_result = FaceScanResult(raw_timestamp, False, None)
            self.first_detection_in_sequence = True
        return self.last_scan_result

    def process_frame(self, frame: VideoService.TimestampedFrame):
        self._current_frame = frame

    def stop(self):
        self._running = False


class FaceScannerService(QObject):
    face_scanned = Signal(FaceScanResult)
    is_scanning_changed = Signal(bool)
    video_available_changed = Signal(bool)
    def __init__(self, 
                 video_service:VideoService,
                 parent=None) -> None:
        super().__init__(parent)
        self._video_service = video_service
        self._video_service.is_available_changed.connect(self._observe_is_active_changed)
        self._video_service.frame_changed.connect(self._handle_frame_captured)
        self._scanner: _Scanner|None = None
        
        self._threadpool = QThreadPool()
        self._last_scan_res:FaceScanResult|None = None
        if video_service.is_available():
            self.start()

        self.app = QApplication.instance()
        print('APPP',self.app)
        if self.app is not None:
            self.app.aboutToQuit.connect(self._observe_app_about_to_quit)

    @Slot()
    def _observe_app_about_to_quit(self):
        print('triggered app.aboutToQuit')
        self.stop()

    def video_service(self):
        return self._video_service

    def video_available(self) -> bool:
        return self._video_service.is_available()

    def is_scanning(self) -> bool:
        if self._scanner is None:
            return False
        return self._scanner.is_running()
    
    @Slot(bool)
    def _observe_is_active_changed(self, is_active:bool):
        self.video_available_changed.emit(is_active)

    @Slot(FaceScanResult)
    def _handle_threader_scanner_process_result(self, scan_res:FaceScanResult):
        self._last_scan_res = scan_res
        # print('_handle_threader_scanner_process_result', scan_res)
        self.face_scanned.emit(scan_res)

    def last_scan_result(self):
        return self._last_scan_res

    def start(self):
        if self.is_scanning():
            return

        self._scanner = _Scanner()
        self._scanner.signals.face_scanned.connect(self._handle_threader_scanner_process_result)
        self._scanner.signals.started.connect(self._handle_scanning_started)
        self._scanner.signals.finished.connect(self._handle_scanning_finished)
        self._threadpool.start(self._scanner)

    def stop(self):
        if self._scanner is None:
            print('self._scanner is None')
            return
        print('self._scanner.stop()')
        self._scanner.stop()
        self._threadpool.waitForDone()

    @Slot()
    def _handle_scanning_started(self):
        self.is_scanning_changed.emit(self.is_scanning())
        
    @Slot()
    def _handle_scanning_finished(self):
        self._scanner = None
        self.is_scanning_changed.emit(self.is_scanning())

    @Slot(VideoService.TimestampedFrame)
    def _handle_frame_captured(self, frame:VideoService.TimestampedFrame):
        if self._scanner is not None:
            self._scanner.process_frame(frame)

            
        
