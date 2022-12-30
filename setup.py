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
        "pillow>=8.2.0, <9.0.0",
        "mutwo.ekmelily>=0.8.0, <1.0.0",
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
        "mutwo.core>=1.0.0, <2.0.0",
        "mutwo.music>=0.19.0, <0.21.0",
        # Abjad dependencies
        "abjad>=3.7.0, <3.8.0",
        "abjad-ext-nauert>=3.7.0, <3.8.0",
    ],
    extras_require=extras_require,
    python_requires=">=3.10, <4",
)
