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
                - \espressivo
                \mf
                % OPENING:
                % COMMANDS:
                \once \override Hairpin.circled-tip = ##t
                d'4
                % AFTER:
                % SPANNER_STARTS:
                \<
            % CLOSE_BRACKETS:
            }
            % OPEN_BRACKETS:
            {
                e'4
                % AFTER:
                % SPANNER_STARTS:
                \>
                % OPENING:
                % COMMANDS:
                \once \override Hairpin.circled-tip = ##t
                e'2.
                % AFTER:
                % SPANNER_STARTS:
                \<
                ~
            % CLOSE_BRACKETS:
            }
            % OPEN_BRACKETS:
            {
                % OPENING:
                % COMMANDS:
                \once \override Hairpin.circled-tip = ##t
                e'2
                % AFTER:
                % SPANNER_STARTS:
                \>
                r2
                % AFTER:
                % ARTICULATIONS:
                \!
            % CLOSE_BRACKETS:
            }
        % CLOSE_BRACKETS:
        }
    % CLOSE_BRACKETS:
    }
}
