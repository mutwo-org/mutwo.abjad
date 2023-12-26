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
                \times 2/3
                {
                    c'4
                    c'8
                    ~
                }
            }
            {
                \times 2/3
                {
                    c'8
                    c'4
                }
                r2.
            }
        }
    }
}
