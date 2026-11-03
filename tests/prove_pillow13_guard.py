"""Prove the clipping regression rejects the old lossy fallback on an isolated copy."""
# mutation-residue-guard: isolated
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]
CURRENT = """        line_height = self.__multiline_spacing(draw, font_pil, spacing, stroke_width)
        line_breaks = text.count("\\n")
        lines_height = line_breaks * line_height
        paddings = real_font_size + stroke_width * 2
        height = int(lines_height + paddings)
"""
MUTANT = """        try:
            line_height = draw._multiline_spacing(font_pil, spacing, stroke_width)
            line_breaks = text.count("\\n")
            lines_height = line_breaks * line_height
            paddings = real_font_size + stroke_width * 2
            height = int(lines_height + paddings)
        except AttributeError:
            height = int(bottom - top)
"""


def main():
    with tempfile.TemporaryDirectory(prefix="moviepy-pillow-mutant-") as directory:
        target = Path(directory)
        for name in ("moviepy", "tests", "media"):
            shutil.copytree(ROOT / name, target / name)
        source = target / "moviepy/video/VideoClip.py"
        original = source.read_text()
        if original.count(CURRENT) != 1:
            raise RuntimeError("Spacing implementation moved; review the mutation proof")
        source.write_text(original.replace(CURRENT, MUTANT))
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "-n", sys.argv[1], "tests/test_pillow13_compat.py", "-q"],
            cwd=target, env={**os.environ, "PYTHONPATH": os.pathsep.join(filter(None, (str(target), os.environ.get("PYTHONPATH"))))},
            capture_output=True, text=True, check=False,
        )
        if result.returncode != 1 or "multiline text is clipped" not in result.stdout:
            raise RuntimeError("Mutation was not caught by clipping assertion:\n" + result.stdout + result.stderr)
        print("PASS: the real clipping regression rejects the old Pillow fallback")


if __name__ == "__main__":
    main()
