# i3 window title changer daemon

This is a small daemon for i3wm which connects to it via Unix socket, listens for new window and title change events and change them to something simple based on the user defined rules.


# Rule definitions

There are three parts of a rule:
1. "match method", which is what kind of method do you want to match on.
   This can be:
   - `text`: if the string is anywhere in the title this will match
   - `regex`: a regular expression to match the window title
   - `class`: i3wm has a class for every new window, this matched the exact
              name of that class. You can find such window classes in the
              output of the scirpt.
2. The search phrase or regex or window class (depends on what you choose 
   for the "match method")
3. The simple string for the new window title.

# Rules file

The "rules file" is a simple CSV file, where every line is a new rule. The
columns are in the above listed order. The first match will change the window
title. That's it.
By default it is located in `~/.config/i3/window-title-changer-rules`, but 
you can override it with the `--rules-file` command option.


# Installation

1. Install requirements: `pip install -r requirements.txt`
2. Make a rule file based on the `title-changer-rules.example`
3. Simply start the daemon by running `i3_window_title_changer.py`.  
   If you use systemd, there is an example systemd service unit file, 
   which you can copy to `~/.config/systemd/user/` and start it with 
   `systemctl --user start i3-window-title-changer.service`.
