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
                \mf
                % SPANNER_STARTS:
                ~
                % OPENING:
                % COMMANDS:
                \once \override BendAfter.minimum-length = #3
                \once \override BendAfter.thickness = #'3
                \once \override DurationLine.style = #'none
                c'8
                % AFTER:
                % ARTICULATIONS:
                - \bendAfter #'3
                r8
            % CLOSE_BRACKETS:
            }
        % CLOSE_BRACKETS:
        }
    % CLOSE_BRACKETS:
    }
}
