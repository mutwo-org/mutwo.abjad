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
                - \espressivo
                \once \override Hairpin.circled-tip = ##t
                d'4
                \<
            }
            {
                e'4
                \>
                \once \override Hairpin.circled-tip = ##t
                e'2.
                \<
                ~
            }
            {
                \once \override Hairpin.circled-tip = ##t
                e'2
                \>
                r2
                \!
            }
        }
    }
}
