from .Sensor import Sensor, Roi
import cv2

class FrameUtilis:
    @staticmethod
    def display_roi_sensors(sensors: list[Sensor], frame, frame_copy):
        colown = 0 
        row = 0
        for index, sensor in enumerate(sensors):
            roi: Roi = sensor.get_roi(frame_copy, False)
            frame = roi.overlay_on_frame(frame, roi.roi_frame, row * 50,   120 + (colown * 50))
            row +=1

            if row % 4 == 0 and index != 0:
                colown += 1
                row = 0

    @staticmethod
    def display_all_roi_sensors(sensors: list[Sensor], frame):
        for sensor in sensors:
            if sensor.show:
                cv2.polylines(frame, [sensor.mass_display], isClosed=True, color=sensor.color, thickness=2)
                # cv2.polylines(frame, [sensor.mass_display_check], isClosed=True, color=sensor.color, thickness=2)
                # cv2.polylines(frame, [sensor.massThree], isClosed=True, color=sensor.color, thickness=2)
                # cv2.polylines(frame, [sensor.massCompress], isClosed=True, color=(255,0,255), thickness=2)
                # cv2.polylines(frame, [sensor.massForCheck], isClosed=True, color=sensor.color, thickness=2)

