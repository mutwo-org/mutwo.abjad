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
                R1 * 1
            % CLOSE_BRACKETS:
            }
            % OPEN_BRACKETS:
            {
                c'1
                % AFTER:
                % ARTICULATIONS:
                \mf
            % CLOSE_BRACKETS:
            }
            % OPEN_BRACKETS:
            {
                d'8
                % AFTER:
                % START_BEAM:
                [
                e'8
                % AFTER:
                % STOP_BEAM:
                ]
                % SPANNER_STARTS:
                ~
                e'8
                e'4.
                e'4
            % CLOSE_BRACKETS:
            }
        % CLOSE_BRACKETS:
        }
        % AFTER:
        % COMMANDS:
        \addlyrics { helloT _ i ho -- pe }
    % CLOSE_BRACKETS:
    }
}
