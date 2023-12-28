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
                c'1
                % AFTER:
                % ARTICULATIONS:
                \mf
                % COMMANDS:
                \bar "!"
            % CLOSE_BRACKETS:
            }
            % OPEN_BRACKETS:
            {
                d'2
                r2
            % CLOSE_BRACKETS:
            }
        % CLOSE_BRACKETS:
        }
    % CLOSE_BRACKETS:
    }
}
