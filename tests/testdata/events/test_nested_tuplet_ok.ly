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
                \tempo 4=120
                \time 4/4
                c'2.
                \mf
                \tweak edge-height #'(0.7 . 0)
                \times 4/5
                {
                    c'16
                    c'16
                    c'8
                }
                \tweak edge-height #'(0.7 . 0)
                \times 8/15
                {
                    d'32
                    d'32
                    d'32
                }
            }
        }
    }
}
