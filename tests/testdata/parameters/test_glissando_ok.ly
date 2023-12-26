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
                \override Glissando.thickness = #'3
                \override Glissando.minimum-length = #5
                \override Glissando.breakable = ##t
                \override Glissando.after-line-breaking = ##t
                \once \override DurationLine.style = #'none
                \override Glissando.springs-and-rods = #ly:spanner::set-spacing-rods
                c'8
                [
                \glissando
                d'8
                ]
                ~
            }
            {
                d'2.
                ~
                d'8
                r8
            }
        }
    }
}
