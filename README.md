Meant to go directly into your `~/.claude/rules` folder

Can be done as follows:

```
PATH_TO_CLAUDE="~/.claude"
git clone git@gitlab.com:flywheel-io/scientific-solutions/etc/utils/code-assistant-instructions.git temp
mv temp/flywheel_specific $PATH_TO_CLAUDE/rules
mv temp/general_coding $PATH_TO_CLAUDE/rules
mv CLAUDE.md $PATH_TO_CLAUDE
rm -rf temp
```

OR the files can be symlinked in:

```
PATH_TO_CLAUDE="$HOME/.claude"
CLONE_DIR="<dir/for/repo>"
git clone git@gitlab.com:flywheel-io/scientific-solutions/etc/utils/code-assistant-instructions.git $CLONE_DIR
ln -s $CLONE_DIR/flywheel_specific $PATH_TO_CLAUDE/rules/flywheel_specific
ln -s $CLONE_DIR/general_coding $PATH_TO_CLAUDE/rules/general_coding
ln -s $CLONE_DIR/CLAUDE.md $PATH_TO_CLAUDE/CLAUDE.md
```
