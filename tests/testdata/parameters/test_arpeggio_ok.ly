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
                \arpeggioArrowUp
                \time 4/4
                <cs' e' a'>2
                \mf
                \arpeggio
                ~
                <cs' e' a'>8
                \arpeggioArrowDown
                <cs' e' a'>8
                \arpeggio
                ~
                <cs' e' a'>4
                ~
            }
            {
                <cs' e' a'>4
                r2.
            }
        }
    }
}
