import numpy as np

def adaptive_visual_fusion(
    image_score,
    video_score
):
    image_weight = 0.4
    video_weight = 0.6

    fused_score = (
        image_score * image_weight +
        video_score * video_weight
    )

    return fused_score