Meant to go directly into your `~/.claude/rules` folder

Can be done as follows:

```
PATH_TO_CLAUDE="~/.claude"
git clone git@gitlab.com:flywheel-io/scientific-solutions/etc/utils/code-assistant-instructions.git temp
mv temp/* $PATH_TO_CLAUDE
mv temp/.git $PATH_TO_CLAUDE
rm -rf temp
```

OR the files can be simlinked in