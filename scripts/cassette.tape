Output assets/demo.gif

Set FontSize 32
Set Height 1080
Set Width 1920
Set Framerate 60
Set WaitTimeout 300

Set Shell fish
Set Theme "GruvboxDark"
Set TypingSpeed 100ms

Set Margin 20
Set MarginFill "#83A598"
Set BorderRadius 15

Type "./re"
Tab
Enter
Sleep 1s
Screenshot assets/usage.png
Sleep 1s

Type "# SSH key was already created and added by us"
Sleep 2s
Enter

Up
Sleep 1
Up
Type " -s karun@192.168.182.137 -k ~/.ssh/cs"
Enter
Sleep 1
Type junioradmin
Enter
Wait

Type "# gns3server is now installed :)"
Sleep 5s

Hide
Type "rm ./assets -r"
Enter
Show
