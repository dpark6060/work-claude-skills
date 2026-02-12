Meant to go directly into your `~/.claude/rules` folder

Can be done as follows:

```
PATH_TO_CLAUDE="/Users/davidparker/Documents/Flywheel/Claude/rules"
git clone git@gitlab.com:flywheel-io/scientific-solutions/etc/utils/code-assistant-instructions.git temp
mv temp/* $PATH_TO_CLAUDE
rm -rf temp
```