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
                \grace {
                    d'8
                    e'8
                }
                \tempo 4=120
                c'1
                \mf
            }
            {
                \afterGrace
                c'1
                {
                    d'8
                    e'8
                    f'8
                }
            }
            {
                c'1
            }
            {
                \grace {
                    d'8
                    e'8
                }
                c'1
            }
        }
    }
}
