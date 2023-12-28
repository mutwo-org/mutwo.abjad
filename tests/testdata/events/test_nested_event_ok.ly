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
    \context Score = "Integrating duo"
    <<
        % OPEN_BRACKETS:
        \context PianoStaff = "Piano"
        <<
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
                    %%% \time 4/4 %%%
                    \set PianoStaff.instrumentName = \markup {  \teeny { Piano } }
                    c'4
                    % AFTER:
                    % ARTICULATIONS:
                    \mf
                    d'4
                    e'4
                    f'4
                % CLOSE_BRACKETS:
                }
                % OPEN_BRACKETS:
                {
                    g'4
                    a'4
                    b'4
                    r4
                % CLOSE_BRACKETS:
                }
            % CLOSE_BRACKETS:
            }
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
                    %%% \time 4/4 %%%
                    c2
                    % AFTER:
                    % ARTICULATIONS:
                    \mf
                    c2
                % CLOSE_BRACKETS:
                }
                % OPEN_BRACKETS:
                {
                    c2
                    c2
                % CLOSE_BRACKETS:
                }
            % CLOSE_BRACKETS:
            }
        % CLOSE_BRACKETS:
        >>
        % OPEN_BRACKETS:
        \context Staff = "Violin"
        <<
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
                    \set Staff.instrumentName = \markup {  \teeny { Violin } }
                    \time 4/4
                    es''2
                    % AFTER:
                    % ARTICULATIONS:
                    \mf
                    es''2
                % CLOSE_BRACKETS:
                }
                % OPEN_BRACKETS:
                {
                    es''2
                    es''2
                % CLOSE_BRACKETS:
                }
            % CLOSE_BRACKETS:
            }
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
                    b2
                    % AFTER:
                    % ARTICULATIONS:
                    \mf
                    b2
                % CLOSE_BRACKETS:
                }
                % OPEN_BRACKETS:
                {
                    b2
                    b2
                % CLOSE_BRACKETS:
                }
            % CLOSE_BRACKETS:
            }
        % CLOSE_BRACKETS:
        >>
    % CLOSE_BRACKETS:
    >>
}
