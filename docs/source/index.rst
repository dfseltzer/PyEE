
PyEE: Python Helpers for Engineering
====================================

A collection of generally useful python helper, wrapers, and other things for engineering.  
Relies on Numpy for a bunch of stuff, either using directly or preferably adding wrappers 
to make things easier.

This package makes use of "unit strings" for text input of units, and "value strings" for 
input of values.  The following formatting is used for these strings...

**Unit Strings (see pyee.types.units)**
Unit strings use standard SI base and derived units.  Each component may include 
an exponent using the "^" symbol, and each *unit^exponent* set is separated by a dot (period ".").
Parentheses may be used to group denominator sets.  Spaces should not be used. Some examples include...

* N  = kg.m.s^-2    = kg.m/s^2 = kg.m/(s^2)
* Pa = kg.m^-1.s^-2 = kg/m/s^2 = kg/(m.s^2)

Attempting to write pascals as *kg/m.s^2* is incorrect, as *s^2* is intepreted in the numerator.


**Value Strings**
These strings use the following formatting

``VALUE[PREFIX][ UNIT]``

VALUE
   Any real number that python can interpret.  Must not have spaces.

PREFIX
   Optional standard SI prefix.  See data files SI_prefixes.json for a full list of acceptable items.
   Do not include a space between the value and prefix.

UNIT
   Optional unit string, using unit string formatting.  If supplied, there must be a single space
   preceeding the supplied unit string, and it must be the only space in the value string.

Some examples of acceptable value strings include

* ``100`` -> Integer 100 with no explicit units.
* ``1m`` -> 0.001 with no explicit units.
* ``1e5 m`` -> 100,000 meters
* ``0.1u H`` -> 100 nano Henries


**Subpakages**
Subpackages are listed below...

.. toctree::
   :maxdepth: 1


Math
----

todo


Types
-----

todo
   

Passives
--------

.. automodule:: pyee.passives
   :no-index:

.. autosummary::
   :toctree:
   :recursive:


Package Support Modules
-----------------------
The following modules are not expected to be called directly, but they exist.

Exceptions
^^^^^^^^^^

todo


Utilities
^^^^^^^^^

todo