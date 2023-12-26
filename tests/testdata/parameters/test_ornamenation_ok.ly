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
                c'4
                \mf
                ^ \markup { \vspace #-0.25 { \fontsize #-4 { \rounded-box { 3 \hspace #-0.4 \path #0.25 
                    #'((moveto 0 0)
                      (lineto 0.5 0)
                      (curveto 0.5 0 1.5 1.75 2.5 0)
                      (lineto 3.5 0))}}}}
                ~
                c'16
                r8.
                r2
            }
        }
    }
}
