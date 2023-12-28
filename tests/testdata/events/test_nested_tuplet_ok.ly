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
                % OPEN_BRACKETS:
                \tweak edge-height #'(0.7 . 0)
                \times 4/5
                {
                    c'16
                    c'16
                    c'8
                % CLOSE_BRACKETS:
                }
                % OPEN_BRACKETS:
                \tweak edge-height #'(0.7 . 0)
                \times 8/15
                {
                    d'32
                    d'32
                    d'32
                % CLOSE_BRACKETS:
                }
            % CLOSE_BRACKETS:
            }
        % CLOSE_BRACKETS:
        }
    % CLOSE_BRACKETS:
    }
}
