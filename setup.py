from setuptools import setup, find_packages
import imp


version = imp.load_source('ambiscaper.version', 'ambiscaper/version.py')

setup(
    name='ambiscaper',
    version=version.version,
    description='A library for soundscape synthesis and augmentation',
    author='Justin Salamon & Duncan MacConnell',
    author_email='andres.perez@upf.edu',
    url='https://github.com/andresperezlopez/ambiscaper',
    download_url='https://github.com/andresperezlopez/ambiscaper/releases',
    packages=['ambiscaper'],
    package_data={'ambiscaper': ['namespaces/ambiscaper_sound_event.json', 'namespaces/ambiscaper_recorded_reverb.json','namespaces/ambiscaper_smir_reverb.json']},
    long_description='Ambiscaper: a tool for automatic dataset generation and annotation of reverberant Ambisonics audio',
    keywords='ambisonics audio sound soundscape',
    license='GNU GPLv3.0',
    classifiers=[
            "License :: OSI Approved :: GPL 3",
            "Programming Language :: Python",
            "Development Status :: 3 - Alpha",
            "Intended Audience :: Developers",
            "Intended Audience :: Science/Research",
            "Topic :: Multimedia :: Sound/Audio :: Analysis",
            "Topic :: Multimedia :: Sound/Audio :: Sound Synthesis",
            "Programming Language :: Python :: 2",
            "Programming Language :: Python :: 2.7",
            "Programming Language :: Python :: 3",
            "Programming Language :: Python :: 3.4",
            "Programming Language :: Python :: 3.5",
            "Programming Language :: Python :: 3.6",
        ],
    install_requires=[
        'sox>=1.3.0',
        'jams==0.2.2',
        'pandas==0.19.2'
    ],
    extras_require={
        'docs': [
                'sphinx==1.2.3',  # autodoc was broken in 1.3.1
                'sphinxcontrib-napoleon',
                'sphinx_rtd_theme',
                'numpydoc',
            ],
        'tests': ['backports.tempfile', 'pysoundfile']
    }
)
