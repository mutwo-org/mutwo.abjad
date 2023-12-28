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
                % COMMANDS:
                \tempo 4=120
                % OPENING:
                % COMMANDS:
                \omit Staff.Beam
                \omit Staff.Flag
                \omit Staff.MultiMeasureRest
                \omit Staff.Rest
                \omit Staff.Stem
                \override Staff.Dots.dot-count = #0
                \override Staff.DurationLine.minimum-length = 6
                \override Staff.DurationLine.thickness = 3
                \override Staff.NoteHead.duration-log = 2
                \time 4/4
                R1 * 1
            % CLOSE_BRACKETS:
            }
            % OPEN_BRACKETS:
            {
                c'8
                % AFTER:
                % ARTICULATIONS:
                \mf
                % COMMANDS:
                \-
                d'8
                % AFTER:
                % COMMANDS:
                \-
                s2.
            % CLOSE_BRACKETS:
            }
            % OPEN_BRACKETS:
            {
                s8
                r8
                r4
                e'4
                % AFTER:
                % COMMANDS:
                \-
                d'4
                % AFTER:
                % COMMANDS:
                \-
            % CLOSE_BRACKETS:
            }
            % OPEN_BRACKETS:
            {
                s4
                c'2.
                % AFTER:
                % COMMANDS:
                \-
            % CLOSE_BRACKETS:
            }
            % OPEN_BRACKETS:
            {
                a'4
                % AFTER:
                % COMMANDS:
                \-
                r2.
            % CLOSE_BRACKETS:
            }
        % CLOSE_BRACKETS:
        }
    % CLOSE_BRACKETS:
    }
}
