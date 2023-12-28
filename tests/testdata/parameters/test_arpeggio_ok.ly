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
                \arpeggioArrowUp
                \tempo 4=120
                % OPENING:
                % COMMANDS:
                \time 4/4
                <cs' e' a'>2
                % AFTER:
                % ARTICULATIONS:
                \arpeggio
                \mf
                % SPANNER_STARTS:
                ~
                <cs' e' a'>8
                % BEFORE:
                % COMMANDS:
                \arpeggioArrowDown
                <cs' e' a'>8
                % AFTER:
                % ARTICULATIONS:
                \arpeggio
                % SPANNER_STARTS:
                ~
                <cs' e' a'>4
                % AFTER:
                % SPANNER_STARTS:
                ~
            % CLOSE_BRACKETS:
            }
            % OPEN_BRACKETS:
            {
                <cs' e' a'>4
                r2.
            % CLOSE_BRACKETS:
            }
        % CLOSE_BRACKETS:
        }
    % CLOSE_BRACKETS:
    }
}
