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
    \context Score = "Integrating duo"
    <<
        \context PianoStaff = "Piano"
        <<
            \new Voice
            {
                {
                    \tempo 4=120
                    %%% \time 4/4 %%%
                    \set PianoStaff.instrumentName = \markup {  \teeny { Piano } }
                    c'4
                    \mf
                    d'4
                    e'4
                    f'4
                }
                {
                    g'4
                    a'4
                    b'4
                    r4
                }
            }
            \new Voice
            {
                {
                    \tempo 4=120
                    %%% \time 4/4 %%%
                    c2
                    \mf
                    c2
                }
                {
                    c2
                    c2
                }
            }
        >>
        \context Staff = "Violin"
        <<
            \new Voice
            {
                {
                    \tempo 4=120
                    \time 4/4
                    \set Staff.instrumentName = \markup {  \teeny { Violin } }
                    es''2
                    \mf
                    es''2
                }
                {
                    es''2
                    es''2
                }
            }
            \new Voice
            {
                {
                    \tempo 4=120
                    \time 4/4
                    b2
                    \mf
                    b2
                }
                {
                    b2
                    b2
                }
            }
        >>
    >>
}
