import setuptools  # type: ignore


with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

extras_require = {
    "testing": [
        "nose",
        "coveralls",
        "pillow>=8.2.0, <9.0.0",
        "mutwo.ext-ekmelily>=0.2.0, <1.0.0",
    ]
}

setuptools.setup(
    name="mutwo.ext-abjad",
    version="0.2.0",
    license="GPL",
    description="abjad extension for event based framework for generative art",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Levin Eric Zimmermann",
    author_email="levin.eric.zimmermann@posteo.eu",
    url="https://github.com/mutwo-org/mutwo.ext-abjad",
    project_urls={"Documentation": "https://mutwo.readthedocs.io/en/latest/"},
    packages=[
        package for package in setuptools.find_packages() if package[:5] != "tests"
    ],
    setup_requires=[],
    install_requires=[
        "mutwo>=0.43.2, <1.0.0",
        "mutwo.ext-music>=0.2.0, <1.0.0",
        "abjad-ext-nauert>=3.4.0, <4",
        "abjad>=3.4.0, <4",
        "abjad-ext-rmakers>=3.4.0, <4",
    ],
    extras_require=extras_require,
    python_requires=">=3.9, <4",
)
