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
                <<
                    % OPEN_BRACKETS:
                    \new Voice
                    {
                        % BEFORE:
                        % COMMANDS:
                        \tempo 4=120
                        % OPENING:
                        % COMMANDS:
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
                        % SPANNER_STARTS:
                        ~
                        <
                            \parenthesize
                            g
                            \tweak NoteHead.style #'harmonic
                            g'
                        >16
                    % CLOSE_BRACKETS:
                    }
                % CLOSE_BRACKETS:
                >>
                r8.
                r2
            % CLOSE_BRACKETS:
            }
            % OPEN_BRACKETS:
            {
                r4
                r16
                % OPEN_BRACKETS:
                <<
                    % OPEN_BRACKETS:
                    \new Voice
                    {
                        % BEFORE:
                        % COMMANDS:
                        \once \override Staff.Stem.thickness = 2
                        \once \override Voice.Stem.direction = 1
                        <
                            g
                            \tweak NoteHead.style #'harmonic
                            d'
                        >8.
                        % AFTER:
                        % SPANNER_STARTS:
                        ~
                        % BEFORE:
                        % COMMANDS:
                        \once \override Staff.Stem.thickness = 2
                        \once \override Voice.Stem.direction = 1
                        <
                            g
                            \tweak NoteHead.style #'harmonic
                            d'
                        >8
                    % CLOSE_BRACKETS:
                    }
                    % OPEN_BRACKETS:
                    \new Voice
                    {
                        % BEFORE:
                        % COMMANDS:
                        \once \override NoteColumn #'force-hshift = #1.5
                        \once \override Staff.Stem.thickness = 2
                        \once \override Voice.Stem.direction = -1
                        <
                            d'
                            \tweak NoteHead.style #'harmonic
                            a'
                        >8.
                        % BEFORE:
                        % COMMANDS:
                        \once \override NoteColumn #'force-hshift = #1.5
                        \once \override Staff.Stem.thickness = 2
                        \once \override Voice.Stem.direction = -1
                        <
                            d'
                            \tweak NoteHead.style #'harmonic
                            a'
                        >8
                    % CLOSE_BRACKETS:
                    }
                % CLOSE_BRACKETS:
                >>
                % OPEN_BRACKETS:
                <<
                    % OPEN_BRACKETS:
                    \new Voice
                    {
                        <
                            \tweak NoteHead.style #'harmonic
                            g'
                        >8
                        % AFTER:
                        % SPANNER_STARTS:
                        ~
                        <
                            \tweak NoteHead.style #'harmonic
                            g'
                        >8.
                    % CLOSE_BRACKETS:
                    }
                % CLOSE_BRACKETS:
                >>
                r16
            % CLOSE_BRACKETS:
            }
        % CLOSE_BRACKETS:
        }
    % CLOSE_BRACKETS:
    }
}
