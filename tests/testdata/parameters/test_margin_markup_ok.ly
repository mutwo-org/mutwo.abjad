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
                \set Staff.instrumentName = \markup { test }
                c'4
                \mf
                ~
                c'16
                r8.
                r2
            }
        }
    }
}
