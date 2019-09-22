import setuptools

setuptools.setup(
    name='pyz3rui',
    version='1.1.0',
    author='Feneg',
    description='User interface for pyz3r',
    url='https://www.github.com/feneg/pyz3rui',
    packages=setuptools.find_packages(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
        'Topic :: Games/Entertainment',
        'Topic :: Utilities'],
    entry_points={
        'console_scripts': (
            'pyz3rui = pyz3rui.cli:parser',)},
    install_requires=[
        'pyz3r>=4.0.0']
    )
