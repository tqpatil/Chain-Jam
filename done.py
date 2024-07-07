from cx_Freeze import setup, Executable
executables = [Executable("game.py", icon='bomb.ico')]
Options = {
    'build_exe': {
        'include_files':     ['1.png', '2.png', '3.png', '4.png', 'bg.png', 'bomb.png', 'boom.ogg', 'fuse.ogg', 'goal.png', 'goal2.png', 'log.png', 'reset.ogg', 'TitleScreen.ogg']
    },
}

setup(options=Options,name="Launchpad", version="0.1", description="Launchpad-GameJamGame", executables=executables)
