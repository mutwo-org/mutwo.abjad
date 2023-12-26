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
                ~
                a'8
                a'8
                ~
                ^ \markup \fontsize #-2.4 { \caps Pizz. }
                a'4
                ~
            }
            {
                a'4
                a'2
                ~
                a'8
                a'8
                ~
            }
            {
                a'2
                a'2
                ~
                ^ \markup \fontsize #-2.4 { \caps { \arco \caps Ord. } }
            }
            {
                a'8
                r8
                r2.
            }
        }
    }
}
