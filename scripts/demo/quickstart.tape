# cngx quickstart terminal demo
# Generate: vhs scripts/demo/quickstart.tape
# Windows: scripts/demo/record_quickstart.ps1 (installs MSVC ttyd if needed)

Output docs/assets/quickstart.gif

Set Shell cmd
Set FontFamily "Cascadia Code"
Set FontSize 15
Set Width 1280
Set Height 720
Set Theme "Catppuccin Mocha"
Set Padding 24
Set MarginFill "#0c0f12"
Set Framerate 12
Set TypingSpeed 45ms
Set PlaybackSpeed 1.15
Set WindowBar Colorful
Set CursorBlink false

Type "pip install -e . -q"
Enter
Sleep 4s

Type "cngx quickstart"
Enter
Sleep 7s
