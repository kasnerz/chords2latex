#!/usr/bin/env python3

import argparse
import re

def chord_pattern():
    return r"[A-H][\w#/]{0,5}"

def is_chord(string):
    pattern = re.compile(r"^" + chord_pattern() + r"$")
    return re.match(pattern, string) is not None

def get_line_type(line):
    if line.strip() == "":
        return "EMPTY"

    tokens = line.split()

    if all([is_chord(token) for token in tokens]):
        return "CHORDS"

    # checking length eliminates matching lyrics "verse" while allowing 
    # some flexibility with punctuation etc.
    if re.search(r"verse", line, re.IGNORECASE) and len(line.strip()) < 10:
        return "VERSE_MARKER"

    if re.search(r"chorus", line, re.IGNORECASE) and len(line.strip()) < 10:
        return "CHORUS_MARKER"

    if re.match(r"^[0-9].*", line):
        return "VERSE_BEGIN"

    if re.match(r"^R\w{0,2}:.*", line):
        return "CHORUS_BEGIN"

    return "SIMPLE"


class SongHeader():
    def __init__(self, name, author):
        self.name = name
        self.author = author

    def __str__(self):
        return "\\beginsong{" + self.name + "}[by={\\normalsize " + self.author + "}]"


class SongFooter():
    def __str__(self):
        return "\\endsong"


class Song:
    def __init__(self, name, author):
        self.header = SongHeader(name, author)
        self.parts = []
        self.footer = SongFooter()

    def __str__(self):
        return "\n".join([
            str(self.header), "\n\n".join([str(part) for part in self.parts]),
            str(self.footer)
        ])

    def add(self, part):
        self.parts.append(part)


class SongPart:
    def __init__(self):
        self.lines = []

    def body(self):
        return "\n".join([str(line) for line in self.lines])

    def __str__(self):
        return "\n".join([self.begin(), self.body(), self.end()])

    def add(self, line):
        self.lines.append(line)


class Verse(SongPart):
    def begin(self):
        return "\\beginverse"

    def end(self):
        return "\\endverse"


class Chorus(SongPart):
    def begin(self):
        return "\\beginchorus"

    def end(self):
        return "\\endchorus"

    def __str__(self):
        # chorus repetition
        if len(self.lines) <= 1:
            return "\\refchorus"

        return "\n".join([self.begin(), self.body(), self.end()])


class Chords:
    def __init__(self, to_european=False):
        self.text = ""
        self.chords = []
        self.to_european = to_european

    def __str__(self):
        next_chord_iter = iter(self.chords)
        next_chord = next(next_chord_iter)
        out_str = []
        extra_chords = True

        for i, char in enumerate(self.text):
            pos, chord = next_chord

            # matching the chords with the respective lyrics
            if i == pos:
                out_str.append(str(chord))
                try:
                    next_chord = next(next_chord_iter)
                except StopIteration:
                    # no more chords
                    extra_chords = False

            out_str.append(char)

        # chords located after the end of the line with lyrics
        while extra_chords:
            try:
                pos, chord = next_chord
                out_str.append(str(chord))
                next_chord = next(next_chord_iter)
            except StopIteration:
                extra_chords = False

        out_str = "".join(out_str)
        out_str = out_str.replace("[:", "\\lrep")
        out_str = out_str.replace(":]", "\\rrep")

        return out_str

    def set_text(self, line):
        line = line.rstrip()
        # removing inline markers (chorus: "R:", verse: "1.", "2." etc.)
        line = re.sub(r"R:(\s*.*)", r"  \1", line)
        line = re.sub(r"[0-9]\.(\s*.*)", r"  \1", line)
        self.text = line

    def set_chords(self, line):
        # save chords along with their position for later reconstruction
        self.chords = [(m.start(0), Chord(m.group(0), self.to_european))
                       for m in re.finditer(chord_pattern(), line.rstrip())]


class SimpleLine(Chords):
    def __init__(self):
        self.text = ""

    def __str__(self):
        return self.text


class Chord:
    def __init__(self, chord, to_european):
        self.chord = chord

        if to_european:
            self.chord = self.chord.replace("B", "H").replace("Hb", "B")

    def __str__(self):
        chord = self.chord

        # replace minor chords
        if chord.endswith("m") or chord.endswith("mi"):
            chord = chord.replace("mi", "&").replace("m", "&")

        return f"\\[{chord}]"


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('input', type=str, help="Input file with chords and lyrics")
    parser.add_argument('-n', '--name', type=str, required=True, help="Name of the song")
    parser.add_argument('-a', '--author', type=str, required=True, help="Author of the song")
    parser.add_argument('-o', '--output', type=str, help="Path to the output .tex file")
    parser.add_argument('-e', '--to_european', action="store_true", help="Convert chords to european notation (B->H, Bb->B)")

    args = parser.parse_args()
    song = Song(name=args.name, author=args.author)

    with open(args.input) as fin:
        lines = fin.readlines()

    current_songpart = None
    songline = None

    for i, line in enumerate(lines):
        linetype = get_line_type(line)

        # skip empty lines
        if linetype == "EMPTY":
            # wrap up the current song part
            if current_songpart is not None:
                song.add(current_songpart)
                current_songpart = None
            continue
        # UG-style "full-line" markers
        elif linetype == "VERSE_MARKER":
            current_songpart = Verse()
            continue
        elif linetype == "CHORUS_MARKER":
            current_songpart = Chorus()
            continue
        # line with chords
        elif linetype == "CHORDS":
            songline = Chords(args.to_european)
            songline.set_chords(line)
            continue
        # line with text
        else: 
            # no preceding chords
            if not songline:
                songline = SimpleLine()

            songline.set_text(line)

        # beginning of a verse/chorus without a previous full-line marker
        if current_songpart is None:
            # "inline"/no markers
            if linetype == "VERSE_BEGIN" \
             or linetype == "SIMPLE":
                current_songpart = Verse()
            elif linetype == "CHORUS_BEGIN":
                current_songpart = Chorus()

        if songline is not None:
            current_songpart.add(songline)

            songline = None

    song.add(current_songpart)

    if args.output:
        with open(args.output, "w") as fout:
            fout.write(str(song))
    else:
        print(song)
