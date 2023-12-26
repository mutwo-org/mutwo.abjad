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
                \tweak edge-height #'(0.7 . 0)
                \times 2/3
                {
                    \tempo 4=120
                    \time 4/4
                    c'4
                    \mf
                    c'4
                }
                \tweak edge-height #'(0.7 . 0)
                \times 8/15
                {
                    c'16.
                    ~
                    c'16
                    ~
                    c'16
                    ~
                    c'16
                    ~
                    c'16
                    ~
                    c'16
                }
                \tweak edge-height #'(0.7 . 0)
                \times 4/5
                {
                    c'16
                    c'8.
                }
                r4
            }
        }
    }
}
