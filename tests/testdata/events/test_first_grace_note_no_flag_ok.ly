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
        \with
        {
            \consists Duration_line_engraver
        }
        {
            % OPEN_BRACKETS:
            {
                % BEFORE:
                % OPEN_BRACKETS:
                \grace {
                    % OPENING:
                    % COMMANDS:
                    \omit Staff.Beam
                    \omit Staff.Flag
                    \omit Staff.MultiMeasureRest
                    \omit Staff.Rest
                    \omit Staff.Stem
                    \override Staff.Dots.dot-count = #0
                    \override Staff.NoteHead.duration-log = 2
                    d'8
                % CLOSE_BRACKETS:
                }
                % COMMANDS:
                \tempo 4=120
                % OPENING:
                % COMMANDS:
                \override Staff.DurationLine.minimum-length = 6
                \override Staff.DurationLine.thickness = 3
                c'1
                % AFTER:
                % ARTICULATIONS:
                \mf
                % COMMANDS:
                \-
            % CLOSE_BRACKETS:
            }
        % CLOSE_BRACKETS:
        }
    % CLOSE_BRACKETS:
    }
}
