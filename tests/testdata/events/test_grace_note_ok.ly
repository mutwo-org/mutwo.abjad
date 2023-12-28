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
                % OPEN_BRACKETS:
                \grace {
                    d'8
                    e'8
                % CLOSE_BRACKETS:
                }
                % COMMANDS:
                \tempo 4=120
                c'1
                % AFTER:
                % ARTICULATIONS:
                \mf
            % CLOSE_BRACKETS:
            }
            % OPEN_BRACKETS:
            {
                % OPENING:
                \afterGrace
                c'1
                % AFTER:
                % OPEN_BRACKETS:
                {
                    d'8
                    e'8
                    f'8
                % CLOSE_BRACKETS:
                }
            % CLOSE_BRACKETS:
            }
            % OPEN_BRACKETS:
            {
                c'1
            % CLOSE_BRACKETS:
            }
            % OPEN_BRACKETS:
            {
                % BEFORE:
                % OPEN_BRACKETS:
                \grace {
                    d'8
                    e'8
                % CLOSE_BRACKETS:
                }
                c'1
            % CLOSE_BRACKETS:
            }
        % CLOSE_BRACKETS:
        }
    % CLOSE_BRACKETS:
    }
}
