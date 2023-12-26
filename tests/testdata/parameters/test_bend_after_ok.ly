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
                \once \override BendAfter.thickness = #'3
                \once \override BendAfter.minimum-length = #3
                \once \override DurationLine.style = #'none
                c'8
                - \bendAfter #'3
                r8
            }
        }
    }
}
