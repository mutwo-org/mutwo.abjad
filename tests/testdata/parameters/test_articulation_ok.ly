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
                <c' f'>2
                % AFTER:
                % ARTICULATIONS:
                - \staccato
                \mf
                % SPANNER_STARTS:
                ~
                <c' f'>8
                % AFTER:
                % ARTICULATIONS:
                - \staccato
                <c' f'>8
                % AFTER:
                % ARTICULATIONS:
                - \tenuto
                % SPANNER_STARTS:
                ~
                <c' f'>4
                % AFTER:
                % ARTICULATIONS:
                - \tenuto
                % SPANNER_STARTS:
                ~
            % CLOSE_BRACKETS:
            }
            % OPEN_BRACKETS:
            {
                <c' f'>4
                % AFTER:
                % ARTICULATIONS:
                - \tenuto
                r2.
            % CLOSE_BRACKETS:
            }
        % CLOSE_BRACKETS:
        }
    % CLOSE_BRACKETS:
    }
}
