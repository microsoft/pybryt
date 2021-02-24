Reference Implementation Objects
================================

The ``__init__`` methods of these subclasses automatically add the instances created to a 
singleton list that PyBryt maintains, so assigning them to variables or tracking them further is 
unnecessary unless more advanced reference implementations are being built. This means that when 
marking up code, as below, creating new variables is unnecessary unless further conditions are to
be made later down the line.

