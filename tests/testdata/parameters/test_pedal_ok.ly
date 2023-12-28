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
                a'2
                % AFTER:
                % ARTICULATIONS:
                \mf
                % SPANNER_STARTS:
                \sustainOn
                ~
                a'8
                a'8
                % AFTER:
                % SPANNER_STARTS:
                ~
                a'4
                % AFTER:
                % SPANNER_STARTS:
                ~
            % CLOSE_BRACKETS:
            }
            % OPEN_BRACKETS:
            {
                a'4
                a'2
                % AFTER:
                % SPANNER_STOPS:
                \sustainOff
                % SPANNER_STARTS:
                ~
                a'8
                g'8
                % AFTER:
                % SPANNER_STARTS:
                \unaCorda
                ~
            % CLOSE_BRACKETS:
            }
            % OPEN_BRACKETS:
            {
                g'2
                g'2
                % AFTER:
                % SPANNER_STARTS:
                ~
            % CLOSE_BRACKETS:
            }
            % OPEN_BRACKETS:
            {
                g'8
                g'8
                % AFTER:
                % SPANNER_STOPS:
                \treCorde
                % SPANNER_STARTS:
                ~
                g'2
                r4
            % CLOSE_BRACKETS:
            }
        % CLOSE_BRACKETS:
        }
    % CLOSE_BRACKETS:
    }
}
