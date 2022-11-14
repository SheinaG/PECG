import setuptools

readme = open('README.md', 'r')
README_TEXT = readme.read()
readme.close()

setuptools.setup(
    name="pecg",
    version="0.0.1",
    use_scm_version={
        "root": "..",
        "relative_to": __file__,
        "local_scheme": "node-and-timestamp",
    },
    author="sheina Gendelman",
    author_email="sheina@campus.technion.ac.il",
    description="pecg: a python toolbox for ECG morphological analysis.",
    long_description=README_TEXT,
    long_description_content_type="text/markdown",
    url="https://github.com/SheinaG/PECG",

    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    # package_dir={"": "pecg"},
    packages={"pecg", "pecg/ecg", "pecg/ecg/c_files", "pecg/ecg/wavedet_exe"},
    package_data={
        "pecg": ["*"],
        "pecg/ecg": ["*"],
        "pecg/ecg/c_files": ["*"],
        "pecg/ecg/wavedet_exe": ["*"],
    },
    include_package_data=True,
    python_requires=">=3.6",
    install_requires=["numpy", "mne", "scipy"],
)
