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
                a'2
                \mf
                \sustainOn
                ~
                a'8
                a'8
                ~
                a'4
                ~
            }
            {
                a'4
                a'2
                \sustainOff
                ~
                a'8
                g'8
                \unaCorda
                ~
            }
            {
                g'2
                g'2
                ~
            }
            {
                g'8
                g'8
                \treCorde
                ~
                g'2
                r4
            }
        }
    }
}
