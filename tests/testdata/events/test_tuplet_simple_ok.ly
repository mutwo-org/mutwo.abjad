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
                    d'4
                    e'8
                    f'8
                    g'16
                    a'16
                    % AFTER:
                    % SPANNER_STARTS:
                    ~
                    a'16
                    b'16
                    c''4
                    d''8
                    e''8
                % CLOSE_BRACKETS:
                }
            % CLOSE_BRACKETS:
            }
        % CLOSE_BRACKETS:
        }
    % CLOSE_BRACKETS:
    }
}
