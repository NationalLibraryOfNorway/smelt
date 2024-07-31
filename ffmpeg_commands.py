import re
import os
import Utils


class FFmpegCommands:
    def __init__(self, smelt_instance):
        self.smelt = smelt_instance


def construct_dpx_commands(self):
    """
    Construct FFmpeg commands for DPX file processing.

    This method constructs a set of FFmpeg commands for processing DPX image sequences
    into various video formats including lossless MOV, H.264 MP4, and ProRes MOV.

    Commands:
    - ffmpeg_base: Base FFmpeg command with verbosity and progress options.
    - ffmpeg_dpx: Command to input DPX image sequence and optional audio file.
        - '-f image2': Input format as image sequence.
        - '-vsync 0': Disable frame duplication or dropping.
        - '-framerate': Frame rate for the input sequence.
        - '-start_number 0': Start frame number.
        - '-i': Input file pattern for DPX files.

    Conditional Commands:
    - If audio is included:
        - '-i': Audio file input.
        - '-c:a copy': Copy audio codec without re-encoding.

    Output Commands:
    - Lossless MOV:
        - '-qp 0': Lossless quality.
    - H.264 MP4:
        - '-c:v libx264': Use H.264 codec for video.
        - '-pix_fmt yuv420p': Pixel format.
        - '-vf scale=-2:1080': Scale video to 1080p while preserving aspect ratio.
        - '-preset slow': Encoding speed/quality tradeoff.
        - '-crf 23': Constant rate factor for quality control.
        - '-c:a aac': Use AAC codec for audio.
        - '-b:a 224k': Audio bitrate.
        - '-map 0:v:0': Map first video stream.
        - '-map 1:a:0': Map first audio stream.
    - ProRes MOV:
        - '-c:v prores': Use ProRes codec for video.
        - '-profile:v 3': ProRes 422 HQ profile.
        - '-c:a pcm_s16le': Use PCM audio codec with 16-bit little-endian samples.

    The constructed commands are stored in instance variables:
    - self.ffmpeg_lossless_cmd
    - self.ffmpeg_h264_cmd_direct
    - self.ffmpeg_prores_cmd
    - self.ffmpeg_h264_cmd
    """
    base_filename = os.path.basename(self.images_path)
    prefix = re.match(r'^\D*', base_filename).group()

    start_number = Utils.extract_number(self.images_path)

    ffmpeg_input_pattern = os.path.join(self.folder_path, '{}%06d.dpx'.format(prefix))

    self.ffmpeg_base = [
        self.ffmpeg_path, '-v',
        'info', '-stats',
        '-progress', '-',
        '-report'
    ]

    ffmpeg_dpx = [
        '-f', 'image2',
        '-vsync', '0',
        '-framerate', self.fps,
        '-start_number', str(start_number),
        '-i', ffmpeg_input_pattern,
    ]

    if self.inkluderLydCheckBox.isChecked() and os.path.exists(self.audio_file):
        ffmpeg_dpx.extend(['-i', self.audio_file])
        audio_cmd = ['-c:a', 'copy']
    else:
        audio_cmd = []

    self.ffmpeg_lossless_cmd = (self.ffmpeg_base + self.ffmpeg_hardware_accel + ffmpeg_dpx +
                                self.ffmpeg_encoder + audio_cmd + [
                                    '-preset', 'slow',
                                    '-qp', '0',
                                    self.lossless_mov,
                                    self.proceed_lossless,
                                ])

    if self.inkluderLydCheckBox.isChecked():
        self.ffmpeg_h264_cmd_direct = self.ffmpeg_base + self.ffmpeg_hardware_accel + ffmpeg_dpx + audio_cmd + [
            '-c:v', 'libx264',
            '-pix_fmt', 'yuv420p',
            '-vf', 'scale=-2:1080',
            '-preset', 'slow',
            '-crf', '23',
            '-c:a', 'aac',
            '-b:a', '224k',
            '-map', '0:v:0',
            '-map', '1:a:0',
            self.h264_mp4,
            self.proceed_h264
        ]
    else:
        self.ffmpeg_h264_cmd_direct = self.ffmpeg_base + self.ffmpeg_hardware_accel + ffmpeg_dpx + [
            '-c:v', 'libx264',
            '-pix_fmt', 'yuv420p',
            '-vf', 'scale=-2:1080',
            '-preset', 'slow',
            '-crf', '23',
            '-map', '0:v:0',
            self.h264_mp4,
            self.proceed_h264
        ]

    if Utils.cuda_available():
        self.ffmpeg_prores_cmd = self.ffmpeg_base + [
            '-hwaccel', 'auto',
            '-i', self.temp_mov,
            '-vf', 'scale=-2:1080,format=yuv422p10le',
            '-c:v', 'prores',
            '-profile:v', '3',
            '-vf', 'scale=-2:1080',
            '-c:a', 'pcm_s16le',
            self.prores_mov,
            self.proceed_prores
        ]
        self.ffmpeg_convert = self.ffmpeg_base + [
            '-i', self.lossless_mov,
            '-pix_fmt', 'yuv422p10le',
            '-vf', 'scale=in_color_matrix=bt709:out_color_matrix=bt709',
            self.temp_mov,
            self.proceed_prores
        ]
    else:
        self.ffmpeg_prores_cmd = self.ffmpeg_base + [
            '-hwaccel', 'auto',
            '-i', self.lossless_mov,
            '-vf', 'scale=-2:1080,format=yuv422p10le',
            '-c:v', 'prores',
            '-profile:v', '3',
            '-vf', 'scale=-2:1080',
            '-c:a', 'pcm_s16le',
            self.prores_mov,
            self.proceed_prores
        ]

    self.ffmpeg_h264_cmd = self.ffmpeg_base + self.ffmpeg_hardware_accel + [
        '-i', self.lossless_mov,
    ] + self.ffmpeg_encoder + [
                               '-vf', 'scale=-2:1080',
                               '-pix_fmt', 'yuv420p',
                               '-preset', 'slow',
                               '-crf', '23',
                               '-c:a', 'aac',
                               '-b:a', '224k',
                               self.h264_mp4,
                               self.proceed_h264
                           ]


def construct_mxf_mov_commands(self):
    """
    Construct FFmpeg commands for MXF and MOV file processing.

    This method constructs FFmpeg commands to process MXF and MOV files into lossless MOV,
    H.264 MP4, and ProRes MOV formats.

    Commands:
    - ffmpeg_base: Base FFmpeg command.
    - ffmpeg_video_audio: Input video and optionally audio file.
    - ffmpeg_audio_param: Parameters for audio encoding.

    Output Commands:
    - Lossless MOV:
        - '-qp 0': Lossless quality.
        - '-c:a copy': Copy audio codec without re-encoding.
    - ProRes MOV:
        - '-c:v prores': Use ProRes codec for video.
        - '-profile:v 3': ProRes 422 HQ profile.
        - '-pix_fmt yuv422p10le': 10-bit YUV 4:2:2 pixel format.
        - '-vf scale=-2:1080': Scale video to 1080p while preserving aspect ratio.
        - '-c:a pcm_s16le': Use PCM audio codec with 16-bit little-endian samples.
    - H.264 MP4:
        - '-c:v libx264': Use H.264 codec for video.
        - '-pix_fmt yuv420p': Pixel format.
        - '-preset slow': Encoding speed/quality tradeoff.
        - '-crf 21': Constant rate factor for quality control.
        - '-ac 2': Set number of audio channels to 2.
        - '-b:a 224k': Audio bitrate.

    The constructed commands are stored in instance variables:
    - self.ffmpeg_dcp_cmd
    - self.ffmpeg_dcp_prores
    - self.ffmpeg_dcp_h264_cmd
    - self.ffmpeg_h264_from_prores_cmd
    """
    ffmpeg_base = [self.ffmpeg_path, '-report', ]

    if self.inkluderLydCheckBox.isChecked and self.audio_file:
        ffmpeg_video_audio = ['-i', self.video, '-i', self.audio_file, ]
        ffmpeg_audio_param = [
            '-c:a', 'aac',
            '-b:a', '224k',
        ]
    else:
        ffmpeg_video_audio = ['-i', self.video, ]
        ffmpeg_audio_param = []
    self.ffmpeg_dcp_cmd = ffmpeg_base + self.ffmpeg_hardware_accel + ffmpeg_video_audio + self.ffmpeg_encoder + [
        '-preset', 'slow',
        '-qp', '0',
        '-c:a', 'copy',
        '-v', 'info',
        self.lossless_mov,
        self.proceed_lossless,
    ]
    self.ffmpeg_dcp_prores = ffmpeg_base + self.ffmpeg_hardware_accel + ffmpeg_video_audio + [
        '-c:v', 'prores',
        '-profile:v', '3',
        '-pix_fmt', 'yuv422p10le',
        '-vf', 'scale=-2:1080',
        '-c:a', 'pcm_s16le',
        self.prores_mov,
        self.proceed_prores
    ]
    self.ffmpeg_dcp_h264_cmd = ffmpeg_base + self.ffmpeg_hardware_accel + ffmpeg_video_audio + [
        '-c:v', 'libx264',
        '-pix_fmt', 'yuv420p',
        '-preset', 'slow',
        '-crf', '21',
        '-ac', '2',
    ] + ffmpeg_audio_param + [
                                   '-v', 'info',
                                   self.h264_mp4,
                                   self.proceed_h264
                               ]
    self.ffmpeg_h264_from_prores_cmd = ffmpeg_base + self.ffmpeg_hardware_accel + ffmpeg_video_audio + [
        '-c:v', 'libx264',
        '-vf', 'scale=-2:1080',
        '-pix_fmt', 'yuv420p',
        '-preset', 'slow',
        '-crf', '23',
        '-v', 'info',
        self.h264_mp4,
        self.proceed_h264
    ]


def construct_audio_commands(self):
    """
    Construct FFmpeg commands for audio file processing.

    This method constructs FFmpeg commands to process audio files into AAC and PCM formats.

    Commands:
    - ffmpeg_audio_cmd: Command to convert audio to AAC format.
        - '-i': Input audio file.
        - '-c:a aac': Use AAC codec for audio.
        - '-b:a 192k': Audio bitrate.
        - '-vn': Disable video.
    - ffmpeg_lossless_audio_cmd: Command to convert audio to PCM format.
        - '-i': Input audio file.
        - '-c:a pcm_s16le': Use PCM audio codec with 16-bit little-endian samples.
        - '-vn': Disable video.

    The constructed commands are stored in instance variables:
    - self.ffmpeg_audio_cmd
    - self.ffmpeg_lossless_audio_cmd
    """
    self.ffmpeg_audio_cmd = [
        self.ffmpeg_path,
        '-report',
        '-i', self.audio_file,
        '-c:a', 'aac',
        '-b:a', '192k',
        '-vn',
        '-v', 'info',
        self.h264_mp4,
        self.proceed_h264
    ]
    self.ffmpeg_lossless_audio_cmd = [
        self.ffmpeg_path,
        '-report',
        '-i', self.audio_file,
        '-c:a', 'pcm_s16le',
        '-vn',
        '-v', 'info',
        self.lossless_mov,
        self.proceed_lossless
    ]