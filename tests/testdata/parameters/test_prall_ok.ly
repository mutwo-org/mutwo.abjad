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
                ~
                ^\prall
                c'8
                r8
            }
        }
    }
}
