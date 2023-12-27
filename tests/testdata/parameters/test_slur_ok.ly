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
                c'4
                \mf
                (
                d'4
                e'4
                d'4
            }
            {
                c'4
                )
                r4
                c'4
                (
                d'4
            }
            {
                c'4
                )
                r2.
            }
        }
    }
}
