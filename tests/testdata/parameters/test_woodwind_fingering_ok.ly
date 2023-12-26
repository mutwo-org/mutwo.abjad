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
                ^\markup 
                \override #'(size . 0.7)
                {
                    \woodwind-diagram
                    #'alto-saxophone
                    #'((cc . (one two three four six))
                       (lh . (low-bes))
                       (rh . (low-c high-fis)))
                }
                c'8
                r8
            }
        }
    }
}
