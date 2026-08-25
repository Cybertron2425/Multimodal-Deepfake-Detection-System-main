def final_multimodal_fusion(
    visual_score,
    audio_score
):

    final_score = (
        0.60 * visual_score +
        0.40 * audio_score
    )

    prediction = (
        "Fake"
        if final_score >= 0.5
        else "Real"
    )

    confidence = (
        final_score
        if prediction == "Fake"
        else 1 - final_score
    )

    return {
        "prediction": prediction,
        "confidence": round(confidence * 100, 2),
        "final_score": round(final_score, 4)
    }