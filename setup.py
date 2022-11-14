import setuptools


setuptools.setup(
    name="pecg",
    version="1.1.8",
    use_scm_version={
        "root": "..",
        "relative_to": __file__,
        "local_scheme": "node-and-timestamp",
    },
    author="sheina Gendelman",
    author_email="sheina@campus.technion.ac.il",
    description="pecg: a python toolbox for ECG morphological analysis.",
    long_description="file: README.md",
    long_description_content_type="text/markdown",
    url="https://github.com/pypa/sampleproject",
    project_urls={
        "Bug Tracker": "https://github.com/pypa/sampleproject/issues",
    },
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
