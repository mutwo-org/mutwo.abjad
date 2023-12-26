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
                \grace {
                    \omit Staff.Rest
                    \omit Staff.MultiMeasureRest
                    \omit Staff.Stem
                    \omit Staff.Flag
                    \omit Staff.Beam
                    \override Staff.Dots.dot-count = #0
                    \override Staff.NoteHead.duration-log = 2
                    d'8
                }
                \tempo 4=120
                \override Staff.DurationLine.minimum-length = 6
                \override Staff.DurationLine.thickness = 3
                c'1
                \mf
                \-
            }
        }
    }
}
