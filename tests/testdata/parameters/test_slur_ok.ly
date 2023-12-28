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
                c'4
                % AFTER:
                % ARTICULATIONS:
                \mf
                % SPANNER_STARTS:
                (
                d'4
                e'4
                d'4
            % CLOSE_BRACKETS:
            }
            % OPEN_BRACKETS:
            {
                c'4
                % AFTER:
                % SPANNER_STOPS:
                )
                r4
                c'4
                % AFTER:
                % SPANNER_STARTS:
                (
                d'4
            % CLOSE_BRACKETS:
            }
            % OPEN_BRACKETS:
            {
                c'4
                % AFTER:
                % SPANNER_STOPS:
                )
                r2.
            % CLOSE_BRACKETS:
            }
        % CLOSE_BRACKETS:
        }
    % CLOSE_BRACKETS:
    }
}
