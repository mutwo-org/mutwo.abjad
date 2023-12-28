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
                a'2
                % AFTER:
                % ARTICULATIONS:
                \mf
                % SPANNER_STARTS:
                ~
                a'8
                a'8
                % AFTER:
                % SPANNER_STARTS:
                ~
                % ABSOLUTE_AFTER:
                % COMMANDS:
                ^ \markup \fontsize #-2.4 { \caps Pizz. }
                a'4
                % AFTER:
                % SPANNER_STARTS:
                ~
            % CLOSE_BRACKETS:
            }
            % OPEN_BRACKETS:
            {
                a'4
                a'2
                % AFTER:
                % SPANNER_STARTS:
                ~
                a'8
                a'8
                % AFTER:
                % SPANNER_STARTS:
                ~
            % CLOSE_BRACKETS:
            }
            % OPEN_BRACKETS:
            {
                a'2
                a'2
                % AFTER:
                % SPANNER_STARTS:
                ~
                % ABSOLUTE_AFTER:
                % COMMANDS:
                ^ \markup \fontsize #-2.4 { \caps { \arco \caps Ord. } }
            % CLOSE_BRACKETS:
            }
            % OPEN_BRACKETS:
            {
                a'8
                r8
                r2.
            % CLOSE_BRACKETS:
            }
        % CLOSE_BRACKETS:
        }
    % CLOSE_BRACKETS:
    }
}
