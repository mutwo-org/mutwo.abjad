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
                        \once \override Staff.Stem.thickness = 2
                        \once \override Voice.Stem.direction = 1
                        \tempo 4=120
                        % OPENING:
                        % COMMANDS:
                        \time 4/4
                        <
                            g
                            \tweak NoteHead.style #'harmonic
                            d'
                        >4
                        % AFTER:
                        % ARTICULATIONS:
                        \mf
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
                        >16
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
                        >4
                        % BEFORE:
                        % COMMANDS:
                        \once \override NoteColumn #'force-hshift = #1.5
                        \once \override Staff.Stem.thickness = 2
                        \once \override Voice.Stem.direction = -1
                        <
                            d'
                            \tweak NoteHead.style #'harmonic
                            a'
                        >16
                    % CLOSE_BRACKETS:
                    }
                % CLOSE_BRACKETS:
                >>
                r8.
                r2
            % CLOSE_BRACKETS:
            }
        % CLOSE_BRACKETS:
        }
    % CLOSE_BRACKETS:
    }
}
