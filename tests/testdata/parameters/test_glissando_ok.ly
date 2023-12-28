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
                \once \override DurationLine.style = #'none
                \override Glissando.after-line-breaking = ##t
                \override Glissando.breakable = ##t
                \override Glissando.minimum-length = #5
                \override Glissando.springs-and-rods = #ly:spanner::set-spacing-rods
                \override Glissando.thickness = #'3
                c'8
                % AFTER:
                % START_BEAM:
                [
                % SPANNER_STARTS:
                \glissando
                d'8
                % AFTER:
                % STOP_BEAM:
                ]
                % SPANNER_STARTS:
                ~
            % CLOSE_BRACKETS:
            }
            % OPEN_BRACKETS:
            {
                d'2.
                % AFTER:
                % SPANNER_STARTS:
                ~
                d'8
                r8
            % CLOSE_BRACKETS:
            }
        % CLOSE_BRACKETS:
        }
    % CLOSE_BRACKETS:
    }
}
