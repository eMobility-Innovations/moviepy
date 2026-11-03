"""Release-banner, rotation and alpha behavior for the current FFmpeg bundle."""
import subprocess

import numpy as np
import pytest

from moviepy import ColorClip, VideoFileClip
from moviepy.video.io import ffmpeg_tools
from moviepy.video.io.ffmpeg_reader import FFmpegInfosParser


@pytest.mark.parametrize("function", [ffmpeg_tools.ffmpeg_version, ffmpeg_tools.ffplay_version])
@pytest.mark.parametrize("version,numeric", [("7.0.2-static", "7.0.2"), ("n9.0.2-17-g2a571b6068-20260930", "9.0.2")])
def test_release_version_prefixes(monkeypatch, function, version, numeric):
    result = subprocess.CompletedProcess([], 0, stdout="ffmpeg version " + version + "\n")
    monkeypatch.setattr(ffmpeg_tools.subprocess, "run", lambda *args, **kwargs: result)
    assert function() == (version, numeric)


def test_title_case_rotation_side_data():
    infos = """ffmpeg version n9.0.2
Input #0, mov,mp4,m4a,3gp,3g2,mj2, from 'rotated.mp4':
  Duration: 00:00:02.12, start: 0.000000, bitrate: 18080 kb/s
  Stream #0:0: Video: h264 (High), yuvj420p, 1920x1080, 21.91 fps, 30 tbr, 90k tbn (default)
    Side data:
      Display Matrix: rotation of -90.00 degrees
"""
    result = FFmpegInfosParser(infos, "rotated.mp4").parse()
    assert result["video_rotation"] == 90
    assert result["video_size"] == [1920, 1080]


def test_vp9_alpha_round_trip(tmp_path):
    filename = str(tmp_path / "alpha.webm")
    with ColorClip((16, 16), color=(20, 80, 150), duration=0.5).with_opacity(0.5) as clip:
        clip.write_videofile(filename, codec="libvpx-vp9", fps=2, threads=1, logger=None)
    with VideoFileClip(filename, has_mask=True) as decoded:
        assert decoded.size == [16, 16]
        np.testing.assert_allclose(decoded.mask.get_frame(0), 0.5, atol=0.02)
