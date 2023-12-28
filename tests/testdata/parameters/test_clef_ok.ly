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
                \clef "bass"
                \time 4/4
                c'4
                % AFTER:
                % ARTICULATIONS:
                \mf
                % SPANNER_STARTS:
                ~
                c'16
                r8.
                r2
            % CLOSE_BRACKETS:
            }
        % CLOSE_BRACKETS:
        }
    % CLOSE_BRACKETS:
    }
}
