"""Sesuaikan durasi adegan dengan rekaman narasi, lalu render video bersuara.

Taruh 16 file narasi di folder narasi/ dengan nama 01.mp3 ... 16.mp3
(boleh .wav/.m4a, dan boleh ada teks lain setelah nomornya, misal "01 Subuh itu.mp3").

    python3 narasi.py                 # siapkan timing + audio, render, gabungkan
    python3 narasi.py --no-render     # hanya timing.js + build/narasi.wav
    python3 narasi.py --fps 10        # render cepat untuk cek sinkron

Cara kerja: setiap potongan narasi punya satu adegan (lihat NARASI.md).
Kalau narasinya lebih panjang dari adegan, adegan itu diperlambat secara
merata sampai narasi selesai + jeda. Adegan tidak pernah dipersingkat,
jadi jeda hening yang memang disengaja tetap ada.
"""
import argparse, json, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
# batas adegan di video.html (detik); potongan ke-i jatuh di [SCENES[i], SCENES[i+1]]
SCENES = [0, 9, 24, 30, 46, 56, 70, 86, 99, 111, 121, 130, 136.5, 145, 154, 162, 171]
# jeda minimal setelah narasi selesai sebelum adegan berganti (ditambah ±1 dtk
# sebelum potongan berikutnya mulai); setelah #13 sengaja ±7 dtk hening
PAD = {13: 6.0, 16: 3.0}
PAD_DEFAULT = 1.2
RATE = 44100


def sh(*cmd):
    return subprocess.run(cmd, check=True, capture_output=True, text=True).stdout


def duration(path):
    return float(sh('ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', path))


def narasi_starts():
    starts = {}
    for line in open(os.path.join(HERE, 'NARASI.md'), encoding='utf-8'):
        m = re.match(r'^\| (\d+) \| (\d+):(\d+) \|', line)
        if m:
            starts[int(m[1])] = int(m[2]) * 60 + int(m[3])
    return starts


def find_clips(folder):
    clips = {}
    for f in sorted(os.listdir(folder)):
        m = re.match(r'^0*(\d+)\D', f)
        if m and f.lower().endswith(('.mp3', '.wav', '.m4a', '.ogg', '.flac')):
            clips.setdefault(int(m[1]), os.path.join(folder, f))
    return clips


def trim(src, dst):
    # buang hening di awal dan akhir supaya narasi mulai tepat di jamnya
    sil = 'silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.05'
    sh('ffmpeg', '-y', '-loglevel', 'error', '-i', src, '-af',
       f'{sil},areverse,{sil},areverse,aformat=sample_rates={RATE}:channel_layouts=mono', dst)
    return duration(dst)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dir', default=os.path.join(HERE, 'narasi'))
    ap.add_argument('--fps', type=int, default=30)
    ap.add_argument('--out', default=os.path.join(HERE, 'video-taziyah-kimdas.mp4'))
    ap.add_argument('--no-render', action='store_true')
    a = ap.parse_args()

    starts, clips = narasi_starts(), find_clips(a.dir)
    missing = [n for n in range(1, 17) if n not in clips]
    if missing:
        sys.exit(f'File narasi belum lengkap di {a.dir}: nomor {missing}')

    build = os.path.join(HERE, 'build')
    os.makedirs(build, exist_ok=True)
    knots, cues, t_out = [[0, 0]], [], 0.0
    print(' #  adegan        narasi   lama -> baru')
    for n in range(1, 17):
        s0, s1 = SCENES[n - 1], SCENES[n]
        off = starts[n] - s0
        wav = os.path.join(build, f'{n:02d}.wav')
        d = trim(clips[n], wav)
        old = s1 - s0
        new = max(old, off + d + PAD.get(n, PAD_DEFAULT))
        k = new / old
        cues.append((wav, t_out + off * k))
        t_out += new
        knots.append([round(t_out, 3), s1])
        flag = '  (diperlambat x%.2f)' % k if k > 1.001 else ''
        print(f'{n:2d}  {s0:5.1f}-{s1:5.1f}  {d:5.2f}s  {old:5.1f} -> {new:5.1f}{flag}')

    with open(os.path.join(HERE, 'timing.js'), 'w') as f:
        f.write('// Dibuat oleh narasi.py: peta waktu video bersuara -> waktu animasi asli.\n')
        f.write(f'window.WARP = {json.dumps(knots)};\n')
    print(f'Durasi baru: {int(t_out // 60)}:{t_out % 60:04.1f}')

    # satu jalur narasi utuh, setiap potongan diletakkan di jam mulainya
    inputs, parts = [], []
    for i, (wav, at) in enumerate(cues):
        inputs += ['-i', wav]
        ms = int(round(at * 1000))
        parts.append(f'[{i}]adelay={ms}:all=1[d{i}]')
    mix = ''.join(f'[d{i}]' for i in range(len(cues)))
    graph = ';'.join(parts) + f';{mix}amix=inputs={len(cues)}:normalize=0,apad=whole_dur={t_out:.3f},' \
        'loudnorm=I=-16:TP=-1.5:LRA=11,aformat=sample_rates=44100[out]'
    track = os.path.join(build, 'narasi.wav')
    sh('ffmpeg', '-y', '-loglevel', 'error', *inputs, '-filter_complex', graph, '-map', '[out]',
       '-t', f'{t_out:.3f}', track)
    print('Audio narasi:', track)
    if a.no_render:
        return

    silent = os.path.join(build, 'video-tanpa-suara.mp4')
    subprocess.run(['node', os.path.join(HERE, 'render.js'), 'video', silent, str(a.fps)], check=True)
    sh('ffmpeg', '-y', '-loglevel', 'error', '-i', silent, '-i', track, '-map', '0:v', '-map', '1:a',
       '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-t', f'{duration(silent):.3f}', '-movflags', '+faststart', a.out)
    print('Selesai:', a.out)


if __name__ == '__main__':
    main()
