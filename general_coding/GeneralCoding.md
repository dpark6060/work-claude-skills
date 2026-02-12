# Data

## Data objects
 - simple data objects can be passed around directly or declared as local, one off variables (Lists
   of integers, single level dictionary where the key names are not important)
 - Complex data objects should be defined using dataclasses or a pydantic baseclass, especially if
   the keys in a dictionary are referenced by name in other parts of the code. 

