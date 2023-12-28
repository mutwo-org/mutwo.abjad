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
                b'2
                % AFTER:
                % STEM_TREMOLOS:
                :16
                % ARTICULATIONS:
                \mf
                % SPANNER_STARTS:
                ~
                b'8
                % AFTER:
                % STEM_TREMOLOS:
                :32
                r8
                r4
            % CLOSE_BRACKETS:
            }
        % CLOSE_BRACKETS:
        }
    % CLOSE_BRACKETS:
    }
}
