from mutwo import core_utilities


class ModuleImportTest(core_utilities.ModuleImportTest):
    module_name_list = r"""
abjad_converters
abjad_parameters
abjad_version""".strip().splitlines()
