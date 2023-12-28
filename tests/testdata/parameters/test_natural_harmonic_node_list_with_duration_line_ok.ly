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
                % OPEN_BRACKETS:
                <<
                    % OPEN_BRACKETS:
                    \new Voice
                    \with
                    {
                        \consists Duration_line_engraver
                    }
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
                        <
                            \parenthesize
                            g
                            \tweak NoteHead.style #'harmonic
                            g'
                        >4
                        % AFTER:
                        % ARTICULATIONS:
                        \mf
                        % COMMANDS:
                        \-
                    % CLOSE_BRACKETS:
                    }
                % CLOSE_BRACKETS:
                >>
                s16
                r8.
                % AFTER:
                % STOP_BEAM:
                ]
                r2
            % CLOSE_BRACKETS:
            }
            % OPEN_BRACKETS:
            {
                r4
                r16
                % AFTER:
                % START_BEAM:
                [
                % OPEN_BRACKETS:
                <<
                    % OPEN_BRACKETS:
                    \new Voice
                    \with
                    {
                        \consists Duration_line_engraver
                    }
                    {
                        % BEFORE:
                        % COMMANDS:
                        \once \override Staff.Stem.duration-log = 2
                        \once \undo \omit Staff.Stem

                        \once \override Staff.Stem.thickness = 2
                        \once \override Voice.Stem.direction = 1
                        <
                            g
                            \tweak NoteHead.style #'harmonic
                            d'
                        >8.
                        % AFTER:
                        % STOP_BEAM:
                        ]
                        % COMMANDS:
                        \-
                    % CLOSE_BRACKETS:
                    }
                    % OPEN_BRACKETS:
                    \new Voice
                    \with
                    {
                        \consists Duration_line_engraver
                    }
                    {
                        % BEFORE:
                        % COMMANDS:
                        \once \override NoteColumn #'force-hshift = #1.5
                        \once \override Staff.Stem.duration-log = 2
                        \once \undo \omit Staff.Stem

                        \once \override Staff.Stem.thickness = 2
                        \once \override Voice.Stem.direction = -1
                        <
                            d'
                            \tweak NoteHead.style #'harmonic
                            a'
                        >8.
                        % AFTER:
                        % COMMANDS:
                        \-
                    % CLOSE_BRACKETS:
                    }
                % CLOSE_BRACKETS:
                >>
                s8
                % OPEN_BRACKETS:
                <<
                    % OPEN_BRACKETS:
                    \new Voice
                    \with
                    {
                        \consists Duration_line_engraver
                    }
                    {
                        <
                            \tweak NoteHead.style #'harmonic
                            g'
                        >8
                        % AFTER:
                        % STOP_BEAM:
                        ]
                        % COMMANDS:
                        \-
                    % CLOSE_BRACKETS:
                    }
                % CLOSE_BRACKETS:
                >>
                s8.
                r16
            % CLOSE_BRACKETS:
            }
        % CLOSE_BRACKETS:
        }
    % CLOSE_BRACKETS:
    }
}
