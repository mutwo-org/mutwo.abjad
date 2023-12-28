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
                % COMMANDS:
                ^\markup 
                \override #'(size . 0.7)
                {
                    \woodwind-diagram
                    #'alto-saxophone
                    #'((cc . (one two three four six))
                       (lh . (low-bes))
                       (rh . (low-c high-fis)))
                }
                c'8
                r8
            % CLOSE_BRACKETS:
            }
        % CLOSE_BRACKETS:
        }
    % CLOSE_BRACKETS:
    }
}
