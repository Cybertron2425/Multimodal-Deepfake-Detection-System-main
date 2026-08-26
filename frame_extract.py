import cv2, os

video_paths = [
    r"C:\Users\Amit Gupta\Downloads\WhatsApp Video 2026-08-20 at 12.53.22 PM.mp4",
    r"C:\Users\Amit Gupta\Downloads\WhatsApp Video 2026-08-25 at 7.55.30 PM.mp4",
    r"C:\Users\Amit Gupta\OneDrive\Pictures\Camera Roll\WIN_20260826_12_43_15_Pro.mp4",
]

os.makedirs("my_real_frames", exist_ok=True)

for video_index, path in enumerate(video_paths):
    if not os.path.exists(path):
        print(f"SKIPPED (not found): {path}")
        continue

    cap = cv2.VideoCapture(path)
    i = 0
    saved = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        if i % 5 == 0:
            cv2.imwrite(f"my_real_frames/v{video_index}_frame_{i}.jpg", frame)
            saved += 1
        i += 1
    cap.release()
    print(f"Done: {path} -> {saved} frames saved")

print("ALL DONE")