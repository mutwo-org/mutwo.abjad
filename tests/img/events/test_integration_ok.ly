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
                \set Staff.instrumentName = \markup { Magic Instr }
                <c' f' a' d'>2.
                \mf
                a'4
            }
            {
                \times 2/3
                {
                    g'8
                    \snappizzicato
                    es'8
                    \fff
                    <fqs' bf' bqf'>8
                }
                c'2.
                \mf
            }
            {
                R1 * 1
            }
            {
                ds'2.
                \fermata
                - \tweak bound-details.left.text \markup \concat { acc. \hspace #0.5 }
                \startTextSpan
                r4
            }
            {
                r8
                [
                \ottava -1
                d8
                ]
                ~
                ^ \markup \fontsize #-2.4 { \caps S.T. }
                d2
                ~
                d8
                [
                \ottava 0
                r8
                \stopTextSpan
                ]
            }
            {
                \tempo 4=130
                r8
                [
                \ottava -2
                b,,8
                ]
                ~
                b,,2.
                ~
            }
            {
                b,,2
                ~
                b,,8
                [
                \ottava 0
                cs''8
                ]
                ~
                ^ \markup \fontsize #-2.4 { \caps Pizz. }
                cs''8
                [
                g''8
                ]
            }
            {
                \time 3/4
                R4 * 3
                \stopTextSpan
            }
            {
                \tempo 4=100
                \time 6/8
                c'4
                - \tweak bound-details.left.text \markup \concat { rit. \hspace #0.5 }
                \startTextSpan
                c'8
                ~
                c'8
                c'4
            }
            {
                \time 3/4
                c'4
                c'4
                c'4
            }
        }
    }
}
