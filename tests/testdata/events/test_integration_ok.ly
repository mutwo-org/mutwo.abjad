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
    % OPEN_BRACKETS:
    \new Staff
    {
        % OPEN_BRACKETS:
        \new Voice
        {
            % OPEN_BRACKETS:
            {
                % BEFORE:
                % COMMANDS:
                \tempo 4=120
                % OPENING:
                % COMMANDS:
                \set Staff.instrumentName = \markup { Magic Instr }
                \time 4/4
                <c' f' a' d'>2.
                % AFTER:
                % ARTICULATIONS:
                \mf
                a'4
            % CLOSE_BRACKETS:
            }
            % OPEN_BRACKETS:
            {
                % OPEN_BRACKETS:
                \times 2/3
                {
                    g'8
                    % AFTER:
                    % COMMANDS:
                    \snappizzicato
                    es'8
                    % AFTER:
                    % ARTICULATIONS:
                    \fff
                    <fqs' bf' bqf'>8
                % CLOSE_BRACKETS:
                }
                c'2.
                % AFTER:
                % ARTICULATIONS:
                \mf
            % CLOSE_BRACKETS:
            }
            % OPEN_BRACKETS:
            {
                R1 * 1
            % CLOSE_BRACKETS:
            }
            % OPEN_BRACKETS:
            {
                ds'2.
                % AFTER:
                % ARTICULATIONS:
                \fermata
                % SPANNER_STARTS:
                - \tweak bound-details.left.text \markup \concat { acc. \hspace #0.5 }
                \startTextSpan
                r4
            % CLOSE_BRACKETS:
            }
            % OPEN_BRACKETS:
            {
                r8
                % AFTER:
                % START_BEAM:
                [
                % BEFORE:
                % COMMANDS:
                \ottava -1
                d8
                % AFTER:
                % STOP_BEAM:
                ]
                % SPANNER_STARTS:
                ~
                % ABSOLUTE_AFTER:
                % COMMANDS:
                ^ \markup \fontsize #-2.4 { \caps S.T. }
                d2
                % AFTER:
                % SPANNER_STARTS:
                ~
                d8
                % AFTER:
                % START_BEAM:
                [
                % BEFORE:
                % COMMANDS:
                \ottava 0
                r8
                % AFTER:
                % SPANNER_STOPS:
                \stopTextSpan
                % STOP_BEAM:
                ]
            % CLOSE_BRACKETS:
            }
            % OPEN_BRACKETS:
            {
                % BEFORE:
                % COMMANDS:
                \tempo 4=130
                r8
                % AFTER:
                % START_BEAM:
                [
                % BEFORE:
                % COMMANDS:
                \ottava -2
                b,,8
                % AFTER:
                % STOP_BEAM:
                ]
                % SPANNER_STARTS:
                ~
                b,,2.
                % AFTER:
                % SPANNER_STARTS:
                ~
            % CLOSE_BRACKETS:
            }
            % OPEN_BRACKETS:
            {
                b,,2
                % AFTER:
                % SPANNER_STARTS:
                ~
                b,,8
                % AFTER:
                % START_BEAM:
                [
                % BEFORE:
                % COMMANDS:
                \ottava 0
                cs''8
                % AFTER:
                % STOP_BEAM:
                ]
                % SPANNER_STARTS:
                ~
                % ABSOLUTE_AFTER:
                % COMMANDS:
                ^ \markup \fontsize #-2.4 { \caps Pizz. }
                cs''8
                % AFTER:
                % START_BEAM:
                [
                g''8
                % AFTER:
                % STOP_BEAM:
                ]
            % CLOSE_BRACKETS:
            }
            % OPEN_BRACKETS:
            {
                % OPENING:
                % COMMANDS:
                \time 3/4
                R4 * 3
                % AFTER:
                % SPANNER_STOPS:
                \stopTextSpan
            % CLOSE_BRACKETS:
            }
            % OPEN_BRACKETS:
            {
                % BEFORE:
                % COMMANDS:
                \tempo 4=100
                % OPENING:
                % COMMANDS:
                \time 6/8
                c'4
                % AFTER:
                % SPANNER_STARTS:
                - \tweak bound-details.left.text \markup \concat { rit. \hspace #0.5 }
                \startTextSpan
                c'8
                % AFTER:
                % SPANNER_STARTS:
                ~
                c'8
                c'4
            % CLOSE_BRACKETS:
            }
            % OPEN_BRACKETS:
            {
                % OPENING:
                % COMMANDS:
                \time 3/4
                c'4
                c'4
                c'4
            % CLOSE_BRACKETS:
            }
        % CLOSE_BRACKETS:
        }
    % CLOSE_BRACKETS:
    }
}
