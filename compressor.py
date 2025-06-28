import subprocess
import os
import time

def get_video_duration(input_path):
    try:
        cmd = [
            'ffprobe', '-v', 'error',
            '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1',
            input_path
        ]
        duration = float(subprocess.check_output(cmd, stderr=subprocess.PIPE))
        return duration
    except:
        return max(os.path.getsize(input_path) / (1024 * 1024), 60)

def compress_video(input_path, output_path):
    time.sleep(1)
    duration = get_video_duration(input_path)
    original_size = os.path.getsize(input_path)
    target_size = original_size * 0.5
    target_bitrate = int((target_size * 8) / (duration * 1024))
    target_bitrate = max(500, min(target_bitrate, 8000))

    cmd = [
        'ffmpeg', '-y',
        '-i', input_path,
        '-c:v', 'libx264',
        '-crf', '26',
        '-preset', 'fast',
        '-vf', 'scale=trunc(iw/2)*2:trunc(ih/2)*2',
        '-c:a', 'aac',
        '-b:a', '96k',
        '-movflags', '+faststart',
        '-fs', str(int(target_size)),
        output_path
    ]

    subprocess.run(cmd, check=True, stderr=subprocess.PIPE)
    return True
