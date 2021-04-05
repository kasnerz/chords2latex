# chords2latex

Converts chords from:
- [ultimate-guitar.com](https://ultimate-guitar.com)
- [pisnicky-akordy.cz](https://pisnicky-akordy.cz)
- (and many other sources using the same notation)

to the notation used in the [songs](http://songs.sourceforge.net) LaTeX package.

## Usage

1. Copy the chords and lyrics from a web page.
2. Paste them into a text file.
3. Use the script to convert the file into LaTeX:
```bash
  ./chords2latex.py <input_file> -n <name> -a <author> -o <output_file>`
```
**Flags**
 - `-n` name of the song 
 - `-a` author of the song
 - `-o` path to the output `.tex` file
 - `-e` convert *B* and *Bb* to european notation (*H* and *B*)

## Example


- input (just a snippet, see [sample.txt](sample.txt) for the full version)
```
[Verse 1]
  C       Bm7          E7              Am     Am/G
Yesterday   all my troubles seemed so far away   
F       G7                    C           C/B Am   D7       F C C
Now it looks as though they're here to stay oh I believe in yesterday
```
- command for converting the file
```bash
./chords2latex.py sample.txt -n "Yesterday" -a "The Beatles" -o yesterday.tex -e
```

- result
```latex
\beginsong{Yesterday}[by={\normalsize The Beatles}]
\beginverse
Ye\[C]sterday \[Hm7]  all my trou\[E7]bles seemed so f\[A&]ar away\[Am/G]
\[F]Now it l\[G7]ooks as though they're\[C] here to sta\[C/H]y oh\[A&] I be\[D7]lieve in \[F]ye\[C]st\[C]erday
\endverse
\endsong
```

The file can be included in a LaTeX document and compiled with the [songs](http://songs.sourceforge.net) package. 

## Disclaimer
The script works the best when used together with my [songbook](https://github.com/kasnerz/songbook).


I made the script for my personal use and I provide no guarantees whatsoever that it's gonna work in your case. I hope it will help, though ;) 

![License: CC BY-NC-SA 4.0](https://licensebuttons.net/l/by-nc-sa/4.0/80x15.png)
