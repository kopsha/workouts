#!/usr/bin/env python3
import yaml
import gzip
import shutil

from faker import Faker
from time import perf_counter_ns


def fake_channels(count=2500):
    faker = Faker()
    channels = list()
    for i in range(count):
        fake_channel = {
            "id": faker.uuid4(),
            "name": f"#{i} {faker.bs().title()}",
            "oboChannelId": f"oboId{faker.pyint()}",
            "drmContentId": faker.uuid4(),
            "cleanupThreshold": faker.license_plate(),
            "intendedTrackTypeId": faker.uuid4(),
            "interimManifestDuration": faker.ssn(),
            "interimManifestTime": [0, 15, 30, 45],
            "manifestUrls": [
                f"http://{faker.ipv4()}{faker.file_path(depth=4)}",
                f"http://{faker.ipv4()}{faker.file_path(depth=4)}",
            ],
            "packagerId": f"pack{faker.pyint(max_value=9)}",
            "sourceId": f"sourceId{faker.pyint(max_value=9)}",
            "swmLength": "PT2H",
            "tenantIds": [faker.country_code().lower()],
            "updatePeriod": "PT7S",
        }
        channels.append(fake_channel)
    return channels


def blow_up_channels(use_config_file, fake_config_file):
    with open(use_config_file, "rt") as file:
        config = yaml.safe_load(file)

    config["channels"] = fake_channels(2500)

    with open(fake_config_file, "wt") as outfile:
        yaml.safe_dump(config, outfile)

    print("Done, faked", len(config["channels"]), "channels.")


def compress(text_file, zipped_file):
    with open(text_file, "rt") as file:
        content = file.read()

    clear_buffer = content.encode("utf-8")

    ref_ns = perf_counter_ns()
    pressed_buffer = gzip.compress(clear_buffer)
    end_ns = perf_counter_ns()

    with open(zipped_file, "wb") as zipped:
        zipped.write(pressed_buffer)

    print(f"Read  {len(clear_buffer):12,} bytes")
    print(f"Wrote {len(pressed_buffer):12,} bytes")
    ratio = len(pressed_buffer) / len(clear_buffer)
    print(f"Ratio: {100 * ratio:.2f}%")
    print(f"Compression took {(end_ns - ref_ns) / 1_000_000:.3f} ms")


def is_gz_file(filepath):
    with open(filepath, "rb") as test_file:
        return test_file.read(2) == b"\x1f\x8b"


def smart_load(filename):
    if is_gz_file(filename):
        print("..: gzipped")

        with open(filename, "rb") as zipfile:
            content = zipfile.read()

        ref_ns = perf_counter_ns()
        buffer = gzip.decompress(content)
        end_ns = perf_counter_ns()
        text = buffer.decode("utf-8")

        print(f"Decompression took {(end_ns - ref_ns) / 1_000_000:.3f} ms")

        with open(filename + ".check", "wt") as outfile:
            outfile.write(text)

    else:
        print("..: plain text")

        with open(filename, "rt") as textfile:
            text = textfile.read()

    config = yaml.safe_load(text)
    print("loaded config has", len(config["channels"]), "channels")


if __name__ == "__main__":
    blow_up_channels("dummy-config.yaml", "faked-config.yaml")
    compress("faked-config.yaml", "faked-config.yaml.gz")

    print("-- testing plain text load")
    shutil.copy("faked-config.yaml", "test-config.yaml")
    smart_load("test-config.yaml")

    print("-- testing compressed load")
    shutil.copy("faked-config.yaml.gz", "test-config.yaml")
    smart_load("test-config.yaml")
