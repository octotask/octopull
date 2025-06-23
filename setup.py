from setuptools import setup

setup(
    name='auto-fork-sync',
    version='0.1.0',
    py_modules=['auto_fork_sync'],
    install_requires=[
        'PyGithub',
        'GitPython',
        'PyYAML'
    ],
    entry_points='''
        [console_scripts]
        auto-fork-sync=auto_fork_sync:main
    ''',
    author='Your Name',
    author_email='you@example.com',
    description='Automated GitHub fork synchronization tool with configurable merge strategies.',
    license='MIT',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
    ],
)
