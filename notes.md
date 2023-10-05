# fixing tuplet concatenation

- my new test shows the difference between using `self._concatenate_adjacent_tuplets` and not using this method
- generally we should use this method
- we should also add my new test to repo
- but this method is poorly documented and buggy
- we should maybe move it to a dedicated place
- and call it: `rewrite_tuplets`
- maybe `abjad_utilities` is a good place for it
- finally: THIS METHOD SHOULD BE OPTIONAL. in a project with duration lines, this method
  really doesn't matter.

- apart from this there is a high need to rewrite the quantization and the building code,
  because it's not very clean, not very readable, and may be buggy.

- WE NEED MORE LOGS OF THE PROCESS!


# implict registration of indicators

- let's change the implicit registration of abjad parameters to an explicit registration with
  something like a 'register' function!
