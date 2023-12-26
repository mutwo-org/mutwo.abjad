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
                \times 2/3
                {
                    \tempo 4=120
                    \time 4/4
                    c'4
                    \mf
                    d'4
                    e'8
                    f'8
                    g'16
                    a'16
                    ~
                    a'16
                    b'16
                    c''4
                    d''8
                    e''8
                }
            }
        }
    }
}
