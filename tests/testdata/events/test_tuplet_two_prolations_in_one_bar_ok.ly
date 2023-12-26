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
                \times 4/5
                {
                    \tempo 4=120
                    \time 4/4
                    c'8
                    \mf
                    c'8
                    c'8
                    c'4
                }
                \times 2/3
                {
                    c'4
                    d'4
                    d'4
                }
            }
        }
    }
}
