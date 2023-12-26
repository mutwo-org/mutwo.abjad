\version "2.24.2"
\language "english"
\include "lilypond-book-preamble.ly"
#(ly:set-option 'tall-page-formats 'png)
\header
{
    tagline = "---integration-test---"
}
\score
{
    \new Staff
    {
        \new Voice
        \with
        {
            \consists Duration_line_engraver
        }
        {
            {
                \tempo 4=120
                \time 4/4
                \override Staff.DurationLine.minimum-length = 6
                \override Staff.DurationLine.thickness = 3
                \omit Staff.Rest
                \omit Staff.MultiMeasureRest
                \omit Staff.Stem
                \omit Staff.Flag
                \omit Staff.Beam
                \override Staff.Dots.dot-count = #0
                \override Staff.NoteHead.duration-log = 2
                R1 * 1
            }
            {
                c'8
                \mf
                \-
                d'8
                \-
                s2.
            }
            {
                s8
                r8
                r4
                e'4
                \-
                d'4
                \-
            }
            {
                s4
                c'2.
                \-
            }
            {
                a'4
                \-
                r2.
            }
        }
    }
}
