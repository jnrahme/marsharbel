#!/usr/bin/env python3
"""Remux compatible intro and body without changing encoded body packets.
Requires PyAV 17.1.0. Does not approve, upload or publish content.
"""
import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path
import av


def digest(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def packet_hashes(path, kind):
    with av.open(str(path)) as source:
        stream = next(s for s in source.streams if s.type == kind)
        return [hashlib.sha256(bytes(p)).hexdigest() for p in source.demux(stream)
                if p.dts is not None]


def signature(stream):
    c = stream.codec_context
    return (stream.type, c.name, c.extradata, c.width, c.height,
            c.format.name, stream.average_rate) if stream.type == 'video' else (
                stream.type, c.name, c.extradata, c.sample_rate, c.channels)


def glue(intro, body, output, offset, intro_sha, body_sha):
    intro, body, output = map(Path, (intro, body, output))
    if output.exists():
        raise ValueError('Output exists: immutable assets must not be overwritten')
    if digest(intro) != intro_sha or digest(body) != body_sha:
        raise ValueError('Source hash mismatch')
    offset = Fraction(str(offset))
    with av.open(str(intro)) as a, av.open(str(body)) as b:
        if {s.type for s in a.streams} != {'video', 'audio'} or len(a.streams) != 2:
            raise ValueError('Exactly one audio and video stream required')
        if len(b.streams) != 2:
            raise ValueError('Body must have exactly two streams')
        sig_a = {s.type: signature(s) for s in a.streams}
        sig_b = {s.type: signature(s) for s in b.streams}
        if sig_a != sig_b:
            raise ValueError('Incompatible codecs or extradata; normalize intro first')
        intro_duration = Fraction(a.duration, av.time_base)
        if offset < intro_duration or offset > intro_duration + Fraction(1, 10):
            raise ValueError('Splice offset must be at end of intro with <=100ms codec guard')
    try:
        with av.open(str(body)) as template, av.open(str(output), 'w',
                         options={'movflags': '+faststart'}) as target:
            streams = {s.type: target.add_stream_from_template(s) for s in template.streams}
            for path, shift in ((intro, Fraction(0)), (body, offset)):
                with av.open(str(path)) as source:
                    for packet in source.demux():
                        if packet.dts is None:
                            continue
                        kind, time_base = packet.stream.type, packet.time_base
                        delta = round(shift / time_base)
                        packet.pts += delta
                        packet.dts += delta
                        packet.stream = streams[kind]
                        packet.time_base = time_base
                        target.mux(packet)
        preservation = {}
        for kind in ('video', 'audio'):
            before, after = packet_hashes(body, kind), packet_hashes(output, kind)
            if after[-len(before):] != before:
                raise ValueError('Body packet payload changed: ' + kind)
            preservation[kind] = {'body_packets': len(before), 'payloads_identical': True}
        last, count = {}, {'video': 0, 'audio': 0}
        with av.open(str(output)) as source:
            for packet in source.demux():
                for frame in packet.decode():
                    kind = packet.stream.type
                    timestamp = frame.pts * frame.time_base
                    if kind in last and timestamp <= last[kind]:
                        raise ValueError('Non-monotonic decoded timestamp: ' + kind)
                    last[kind] = timestamp
                    count[kind] += 1
        return {'sha256': digest(output), 'bytes': output.stat().st_size,
                'intro_sha256': intro_sha, 'body_sha256': body_sha,
                'body_offset_seconds': float(offset), 'preservation': preservation,
                'decoded_frames': count, 'quality_gate': 'pending-independent-review'}
    except Exception:
        output.unlink(missing_ok=True)
        raise


def main():
    parser = argparse.ArgumentParser()
    for name in ('intro', 'body', 'output', 'intro-sha', 'body-sha', 'offset'):
        parser.add_argument('--' + name, required=True)
    args = parser.parse_args()
    proof = glue(args.intro, args.body, args.output, args.offset, args.intro_sha, args.body_sha)
    Path(args.output + '.proof.json').write_text(json.dumps(proof, indent=2) + '\n')
    print(json.dumps(proof))


if __name__ == '__main__':
    main()
