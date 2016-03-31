from setuptools import setup, find_packages
import versioneer

setup(
    name='anaconda-salt-toolkit',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    author='Sean Ross-Ross',
    author_email='srossross@gmail.com',
    url='http://github.com/srossross/anaconda-salt-toolkit',
    description='Anaconda Salt Toolkit',
    packages=find_packages(),
    install_requires=['salt', 'clyent'],
    entry_points={
        'console_scripts': [
            'atool = atool.script:main',
        ]
    },
)
