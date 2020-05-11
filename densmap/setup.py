from setuptools import setup

#def readme():
#    with open('README.md') as readme_file:
#        return readme_file.read()

with open("README.md", "r") as fh:
    long_description = fh.read()
    
configuration = {
    'name' : 'densmap-learn',
    'version': '0.2.0',
    'description' : 'densMAP',
    'long_description' : long_description,
    'long_description_content_type' : "text/markdown",
    'classifiers' : [
        'Intended Audience :: Science/Research',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: C',
        'Programming Language :: Python',
        'Topic :: Software Development',
        'Topic :: Scientific/Engineering',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Operating System :: Unix',
        'Operating System :: MacOS',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.6',
    ],
    'keywords' : 'dimension reduction t-sne manifold density',
    'url' : 'http://github.com/hhcho/densvis',
    'maintainer' : 'Ashwin Narayan',
    'maintainer_email' : 'ashwinn@mit.edu',
    'license' : 'MIT',
    'packages' : ['densmap'],
    'install_requires': ['numpy >= 1.13',
                         'scikit-learn >= 0.16',
                          'scipy >= 0.19',
                         'numba == 0.48.0'],
    'ext_modules' : [],
    'cmdclass' : {},
    'test_suite' : 'nose.collector',
    'tests_require' : ['nose'],
    'package_data' : {'densmap-learn' : ['trial_data.txt']}, 
    'include_package_data' : True, 
    'data_files' : (['trial_data.txt'])
    }

setup(**configuration)
