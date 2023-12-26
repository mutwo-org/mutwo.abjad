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
                <<
                    \new Voice
                    \with
                    {
                        \consists Duration_line_engraver
                    }
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
                        <
                            \parenthesize
                            g
                            \tweak NoteHead.style #'harmonic
                            g'
                        >4
                        \mf
                        \-
                    }
                >>
                s16
                r8.
                ]
                r2
            }
            {
                r4
                r16
                [
                <<
                    \new Voice
                    \with
                    {
                        \consists Duration_line_engraver
                    }
                    {
                        \once \override Staff.Stem.thickness = 2
                        \once \override Voice.Stem.direction = 1
                        \once \override Staff.Stem.duration-log = 2
                        \once \undo \omit Staff.Stem

                        <
                            g
                            \tweak NoteHead.style #'harmonic
                            d'
                        >8.
                        ]
                        \-
                    }
                    \new Voice
                    \with
                    {
                        \consists Duration_line_engraver
                    }
                    {
                        \once \override Staff.Stem.thickness = 2
                        \once \override Voice.Stem.direction = -1
                        \once \override Staff.Stem.duration-log = 2
                        \once \undo \omit Staff.Stem

                        \once \override NoteColumn #'force-hshift = #1.5
                        <
                            d'
                            \tweak NoteHead.style #'harmonic
                            a'
                        >8.
                        \-
                    }
                >>
                s8
                <<
                    \new Voice
                    \with
                    {
                        \consists Duration_line_engraver
                    }
                    {
                        <
                            \tweak NoteHead.style #'harmonic
                            g'
                        >8
                        ]
                        \-
                    }
                >>
                s8.
                r16
            }
        }
    }
}
