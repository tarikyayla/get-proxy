from setuptools import setup

setup(
    name='get-proxy',
    url='https://github.com/tarikyayla/mangareaderlib',
    author='Tarık Yayla',
    author_email='tarik.yayla33@gmail.com',
    packages=['get_proxy'],
    install_requires=['fake-headers','tqdm','requests'],
    version='0.1',
    license='MIT',
    description='Get free proxies for your project',
    long_description=open('README.md').read(),
)
