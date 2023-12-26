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
        {
            {
                <<
                    \new Voice
                    {
                        \tempo 4=120
                        \time 4/4
                        <
                            \parenthesize
                            g
                            \tweak NoteHead.style #'harmonic
                            g'
                        >4
                        \mf
                        ~
                        <
                            \parenthesize
                            g
                            \tweak NoteHead.style #'harmonic
                            g'
                        >16
                    }
                >>
                r8.
                r2
            }
            {
                r4
                r16
                <<
                    \new Voice
                    {
                        \once \override Staff.Stem.thickness = 2
                        \once \override Voice.Stem.direction = 1
                        <
                            g
                            \tweak NoteHead.style #'harmonic
                            d'
                        >8.
                        ~
                        \once \override Staff.Stem.thickness = 2
                        \once \override Voice.Stem.direction = 1
                        <
                            g
                            \tweak NoteHead.style #'harmonic
                            d'
                        >8
                    }
                    \new Voice
                    {
                        \once \override Staff.Stem.thickness = 2
                        \once \override Voice.Stem.direction = -1
                        \once \override NoteColumn #'force-hshift = #1.5
                        <
                            d'
                            \tweak NoteHead.style #'harmonic
                            a'
                        >8.
                        \once \override Staff.Stem.thickness = 2
                        \once \override Voice.Stem.direction = -1
                        \once \override NoteColumn #'force-hshift = #1.5
                        <
                            d'
                            \tweak NoteHead.style #'harmonic
                            a'
                        >8
                    }
                >>
                <<
                    \new Voice
                    {
                        <
                            \tweak NoteHead.style #'harmonic
                            g'
                        >8
                        ~
                        <
                            \tweak NoteHead.style #'harmonic
                            g'
                        >8.
                    }
                >>
                r16
            }
        }
    }
}
