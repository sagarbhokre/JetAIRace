import cv2
from jetcam.csi_camera import CSICamera

def bgr8_to_jpeg(value, quality=75):
    return bytes(cv2.imencode('.jpg', value)[1])


camera = CSICamera(width=1280, height=720)
camera.running = True
camera.unobserve_all()

while True:
    snapshot = camera.value.copy()
    cv2.imshow("CSI Camera Feed", snapshot)
    k = cv2.waitKey(33) & 0xFF
    if k == 27 or k == ord('q'):
        break
