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
                c'4
                % AFTER:
                % ARTICULATIONS:
                \mf
                % MARKUP:
                ^ \markup { \vspace #-0.25 { \fontsize #-4 { \rounded-box { 3 \hspace #-0.4 \path #0.25 
                    #'((moveto 0 0)
                      (lineto 0.5 0)
                      (curveto 0.5 0 1.5 1.75 2.5 0)
                      (lineto 3.5 0))}}}}
                % SPANNER_STARTS:
                ~
                c'16
                r8.
                r2
            % CLOSE_BRACKETS:
            }
        % CLOSE_BRACKETS:
        }
    % CLOSE_BRACKETS:
    }
}
