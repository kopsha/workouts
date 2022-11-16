#!/usr/bin/env python3
from pytube import YouTube, Playlist
from pytube.exceptions import PytubeError
import re
import subprocess


def exec(command):
    """runs shell command and capture the output"""

    result = subprocess.run(command, shell=True, capture_output=True)

    if result.returncode:
        raise RuntimeError(f"Error executing: {command}")

    return result.stdout.decode("utf-8").strip()


has_author_title = re.compile(r"^\s*(.+?)\s*-\s*(.+?)\s*$")
has_separator = re.compile(r"^\s*(.+?)\s*[^a-zA-Z\d\s]\s*(.+?)\s*$")


def aggressive_clean(text):
    drop_words = [
        "audio",
        "music video",
        "LIVE BEDROOM RECORDING",
        "official music video",
        "official audio",
        "official video",
        "official",
        "videoclip oficial",
        "live session",
        "KondZilla",
        "remix remastered",
        "Lyrics Video",
        "Vocal Mix",
        "\*Lyrics in description below\*",
        "\*HIGH QUALITY\*",
        "\[FULL\]",
        "\(HQ\)",
    ]

    drop_all = "(" + "|".join(sorted(drop_words, reverse=True, key=lambda x: len(x))) + ")"
    result = re.sub(drop_all, "", text, flags=re.IGNORECASE)

    result = re.sub("\|+", "-", result)
    result = re.sub(r"[^\w\s\-]+", "", result)
    result = re.sub("-+\s*$", "", result)
    result = re.sub("\s+", " ", result)

    return result.strip().title()

def download_audio(video: YouTube, to_path: str, position: int):
    print(f"Downloading {video.title} [{video.video_id}]")
    audio_streams = video.streams.filter(only_audio=True)
    best_audio = sorted(audio_streams, key=lambda x: int(x.abr[:-4]), reverse=True)[0]
    filename = aggressive_clean(video.title)
    with_extension = ".".join((filename, best_audio.audio_codec))
    best_audio.download(output_path=to_path, filename=with_extension, skip_existing=True)
    print(f"    -> {with_extension}")
    if not best_audio.audio_codec.endswith(".mp3"):
        bitrate = best_audio.abr.replace("bps", "")
        command = f"ffmpeg -i '{to_path}/{with_extension}' -b:a {bitrate} '{to_path}/{position:03d} - {filename}.mp3'"
        exec(command)
        print(f"    => {filename}.mp3")


def main(to_path):
    # video = YouTube("https://www.youtube.com/watch?v=l54K_3gcRIE")
    play = Playlist("https://www.youtube.com/playlist?list=PLCKf_DRH9vw1G5c1S0AXL5XZ8DHAiiBJF")
    for i, video_url in enumerate(play.video_urls):
        if i <= 80:
            continue
        try:
            video = YouTube(video_url, use_oauth=True, allow_oauth_cache=True)

            video.check_availability()
            if video.age_restricted:
                video.bypass_age_gate()

            download_audio(video, to_path, i)

        except PytubeError as err:
            print(f"Video {video.video_id} ({i}), {video.title} cannot be downloaded, reason: {str(err)}.")

    print("done?", len(play.videos))


if __name__ == "__main__":
    from argparse import ArgumentParser

    parser = ArgumentParser("download youtube videos")
    parser.add_argument("--to", dest="path", required=True, help="save files to ...")
    args = parser.parse_args()

    main(args.path.rstrip("/"))
