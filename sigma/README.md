# Sigma

System for loading and verifying problems in a jupyter notebook.

## How to use

To make sigma work,  write a setup script that creates  a file: 

    ~/.ipython/profile_default/startup/startup.py

with content:

```python
from sigma import magic
magic.register()
```