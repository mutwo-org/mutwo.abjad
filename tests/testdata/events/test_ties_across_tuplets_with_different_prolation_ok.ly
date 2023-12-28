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
                % OPEN_BRACKETS:
                \tweak edge-height #'(0.7 . 0)
                \times 2/3
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
                    c'4
                % CLOSE_BRACKETS:
                }
                % OPEN_BRACKETS:
                \tweak edge-height #'(0.7 . 0)
                \times 8/15
                {
                    c'16.
                    % AFTER:
                    % SPANNER_STARTS:
                    ~
                    c'16
                    % AFTER:
                    % SPANNER_STARTS:
                    ~
                    c'16
                    % AFTER:
                    % SPANNER_STARTS:
                    ~
                    c'16
                    % AFTER:
                    % SPANNER_STARTS:
                    ~
                    c'16
                    % AFTER:
                    % SPANNER_STARTS:
                    ~
                    c'16
                % CLOSE_BRACKETS:
                }
                % OPEN_BRACKETS:
                \tweak edge-height #'(0.7 . 0)
                \times 4/5
                {
                    c'16
                    c'8.
                % CLOSE_BRACKETS:
                }
                r4
            % CLOSE_BRACKETS:
            }
        % CLOSE_BRACKETS:
        }
    % CLOSE_BRACKETS:
    }
}
