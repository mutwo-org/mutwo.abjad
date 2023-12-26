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
                \breathe
                c'2.
                \mf
                ~
                c'8
                r8
            }
        }
    }
}
