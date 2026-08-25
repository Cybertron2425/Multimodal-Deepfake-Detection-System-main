from moviepy import VideoFileClip


def extract_audio(video_path, output_audio_path):

    video = VideoFileClip(video_path)

    if video.audio is None:
        video.close()
        return None

    video.audio.write_audiofile(
        output_audio_path,
        codec="pcm_s16le",
        logger=None
    )

    video.close()

    return output_audio_path