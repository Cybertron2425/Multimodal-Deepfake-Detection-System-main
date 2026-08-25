import numpy as np

def select_suspicious_frames(frames, frame_probs, top_k=3):

    if len(frames) == 0:
        return []

    top_idx = np.argsort(frame_probs)[-top_k:]

    return [frames[i] for i in top_idx]