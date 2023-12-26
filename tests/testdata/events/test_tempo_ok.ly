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
                \tempo 2=30-50
                \time 4/4
                c'1
                \mf
            }
            {
                c'1
            }
            {
                c'1
            }
        }
    }
}
