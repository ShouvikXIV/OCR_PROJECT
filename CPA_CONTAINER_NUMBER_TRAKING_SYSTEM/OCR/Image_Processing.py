import cv2
import easyocr
import threading
import time

# OCR reader for English only
reader = easyocr.Reader(['en'])

# IP Camera stream from Raspberry Pi
camera_url = 'http://192.168.0.150:8081/'  # Update with your IP

# Shared frame buffer
latest_frame = None
lock = threading.Lock()
running = True

# Thread 1: Capture frames continuously
def capture_thread():
    global latest_frame, running
    cap = cv2.VideoCapture(camera_url)
    if not cap.isOpened():
        print("❌ Failed to open camera stream")
        running = False
        return

    while running:
        ret, frame = cap.read()
        if ret:
            with lock:
                latest_frame = frame.copy()

    cap.release()

# Thread 2: OCR processing every 0.5 seconds
def ocr_thread():
    global latest_frame, running
    while running:
        time.sleep(0.5)  # Control how frequently OCR runs

        frame_copy = None
        with lock:
            if latest_frame is not None:
                frame_copy = latest_frame.copy()

        if frame_copy is not None:
            results = reader.readtext(frame_copy)

            for (bbox, text, prob) in results:
                if prob > 0.5:
                    (tl, tr, br, bl) = bbox
                    tl = tuple(map(int, tl))
                    br = tuple(map(int, br))
                    cv2.rectangle(frame_copy, tl, br, (0, 255, 0), 2)
                    cv2.putText(frame_copy, text, (tl[0], tl[1] - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                    print(f"OCR: {text} ({prob:.2f})")

            cv2.imshow("EasyOCR (Threaded)", frame_copy)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                running = False
                break

# Start threads
t1 = threading.Thread(target=capture_thread)
t2 = threading.Thread(target=ocr_thread)

t1.start()
t2.start()

t1.join()
t2.join()
cv2.destroyAllWindows()