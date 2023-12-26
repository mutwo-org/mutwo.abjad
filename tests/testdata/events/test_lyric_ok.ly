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
                R1 * 1
            }
            {
                c'1
                \mf
            }
            {
                d'8
                [
                e'8
                ]
                ~
                e'8
                e'4.
                e'4
            }
        }
        \addlyrics { helloT _ i ho -- pe }
    }
}
