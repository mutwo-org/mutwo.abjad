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
                <
                    c'
                    \tweak NoteHead.style #'harmonic
                    f'
                >2.
                % AFTER:
                % ARTICULATIONS:
                \mf
                % SPANNER_STARTS:
                ~
                <
                    c'
                    \tweak NoteHead.style #'harmonic
                    f'
                >8
                r8
            % CLOSE_BRACKETS:
            }
        % CLOSE_BRACKETS:
        }
    % CLOSE_BRACKETS:
    }
}
