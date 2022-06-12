import setuptools  # type: ignore

MAJOR, MINOR, PATCH = 0, 10, 0
VERSION = f"{MAJOR}.{MINOR}.{PATCH}"
"""This project uses semantic versioning.
See https://semver.org/
Before MAJOR = 1, there is no promise for
backwards compatibility between minor versions.
"""

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

extras_require = {
    "testing": [
        "nose",
        "coveralls",
        "pillow>=8.2.0, <9.0.0",
        "mutwo.ext-ekmelily>=0.6.2, <0.7.0",
    ]
}

setuptools.setup(
    name="mutwo.ext-abjad",
    version=VERSION,
    license="GPL",
    description="abjad extension for event based framework mutwo",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Levin Eric Zimmermann",
    author_email="levin.eric.zimmermann@posteo.eu",
    url="https://github.com/mutwo-org/mutwo.ext-abjad",
    project_urls={"Documentation": "https://mutwo.readthedocs.io/en/latest/"},
    packages=[
        package
        for package in setuptools.find_namespace_packages(
            include=["mutwo.*", "mutwo_third_party.*"]
        )
        if package[:5] != "tests"
    ],
    setup_requires=[],
    install_requires=[
        # Mutwo dependencies
        "mutwo.ext-core>=0.59.0, <0.60.0",
        "mutwo.ext-music>=0.16.0, <0.17.0",
        # Abjad dependencies
        "abjad>=3.4.0, <3.5.0",
        "abjad-ext-nauert>=3.4.0, <3.5.0",
    ],
    extras_require=extras_require,
    python_requires=">=3.9, <4",
)
