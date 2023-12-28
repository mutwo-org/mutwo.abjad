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
                \time 4/4
                c'2.
                % AFTER:
                % ARTICULATIONS:
                \fermata
                \mf
                % SPANNER_STARTS:
                ~
                c'8
                % AFTER:
                % START_BEAM:
                [
                c'8
                % AFTER:
                % ARTICULATIONS:
                \longfermata
                % STOP_BEAM:
                ]
                % SPANNER_STARTS:
                ~
            % CLOSE_BRACKETS:
            }
            % OPEN_BRACKETS:
            {
                c'2.
                r4
            % CLOSE_BRACKETS:
            }
        % CLOSE_BRACKETS:
        }
    % CLOSE_BRACKETS:
    }
}
