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
                \times 4/5
                {
                    % BEFORE:
                    % COMMANDS:
                    \tempo 4=120
                    % OPENING:
                    % COMMANDS:
                    \time 4/4
                    c'8
                    % AFTER:
                    % ARTICULATIONS:
                    \mf
                    c'8
                    c'8
                    c'4
                % CLOSE_BRACKETS:
                }
                % OPEN_BRACKETS:
                \times 2/3
                {
                    c'4
                    d'4
                    d'4
                % CLOSE_BRACKETS:
                }
            % CLOSE_BRACKETS:
            }
        % CLOSE_BRACKETS:
        }
    % CLOSE_BRACKETS:
    }
}
