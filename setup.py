import setuptools  # type: ignore

version = {}
with open("mutwo/abjad_version/__init__.py") as fp:
    exec(fp.read(), version)

VERSION = version["VERSION"]

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

extras_require = {
    "testing": [
        "pytest>=7.1.1",
        "mutwo.ekmelily>=0.9.0, <1.0.0",
    ]
}

setuptools.setup(
    name="mutwo.abjad",
    version=VERSION,
    license="GPL",
    description="abjad extension for event based framework mutwo",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Levin Eric Zimmermann",
    author_email="levin.eric.zimmermann@posteo.eu",
    url="https://github.com/mutwo-org/mutwo.abjad",
    project_urls={"Documentation": "https://mutwo-org.github.io"},
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
        "mutwo.core>=2.0.0, <3.0.0",
        "mutwo.music>=0.27.0, <1.0.0",
        # Abjad dependencies
        "abjad>=3.9.0, <3.12.0",
        "abjad-ext-nauert>=3.9.0, <3.12.0",
        # Other dependencies
        "python-ranges>=1.2.0, <2.0.0",
    ],
    extras_require=extras_require,
    python_requires=">=3.10, <4",
)
