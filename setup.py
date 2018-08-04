from distutils.core import setup
import karma

setup(
    name='discord-karma',
    version=karma.__version__,
    description='Karma Bot for Discord',
    author='Harvey Rendell',
    author_email='hjrendell@gmail.com',
    url='https://github.com/Puhapig/discord-karma',
    packages=[
        'karma',
        'karma.cogs',
    ],
    install_requires=[
        'discord.py',
        'sqlalchemy',
        'tzlocal',
    ],
)
