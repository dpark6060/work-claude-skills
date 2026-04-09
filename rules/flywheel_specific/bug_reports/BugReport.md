# Bugs
In flywheel, we encounter bugs.  So many bugs.  It's mostly bugs, honestly.
Because of this, we write a lot of bug reports.  Please help us write bug
reports.  

## Inputs
We will provide the following: 
1. A brief description of the bug in normal language.
2. The exact command that generates the bug
3. The exact output that we get when we encounter the bug.

You may ask for more if you think you need more.  If one of the three above is
not provided, you may ask for it.

If you need SDK documentation for specific objects or calls, you must ask for it.

## Outputs
From there, you will provide the following:
1. A summary of the bug (1 sentence, no more than 255 characters)
2. Steps to reproduce.  Use a few sentences to describe the conditions and the
   provide sample code to execute. See code instructions below for more
   details.
3. Expected Behavior.
4. Observed Behavior
5. Environment.  You can make this part Just the following placeholders:
    - OS:
    - Python Version:
    - Flywheel Instance Version:
    - Flywheel SDK Version:

All output should just be an example file in the augment agent chat, not
actually creating or modifying any files.


## Code Instructions
### Flywheel Client
The flywheel sdk typically needs to initialize a flywheel client, done using an
API key.  Set this as a variable that the tester can change and run.  It is ok
if it's code that' won't technically execute.

```python
import flywheel
API_KEY="<API_KEY>"
client = flywheel.Client(API_KEY)
```

### Flywheel Containers
Sometimes a container is needed (a project, a subject, a file, etc). 
If the bug report specifies that it has to be a specific project, use any IDs or
info provided with the prompt to get those containers.  If the bug is with a
call that's NON-DESTRUCTIVE, meaning it won't alter or delete any data, then you
can simply get example containers like this:
```python
project = fw.projects.find_first()
subject = project.subjects.find_first()
file = subject.files[0]

```

However if there are destructive calls, then set up your own containers.
```python
project = fw.add_project("test_project")
subject = project.add_subject("test_subject")
```

If you need to make a fake file, you can do so like this:
```python
import io
file_contents="abc"
with io.StringIO(file_contents) as fd:
    fsize = len(file_contents)
    f = fw.upload_file_to_container(parent.id, flywheel.FileSpec(name, fd, size=fsize))
```

Or if you don't need actual objects in flywheel, you can create dummies of them
using the API models. 

The code should also have code to delete anything it creates if you have to do
that, but have that code commented out so that the user can delete it when they
need to. 



