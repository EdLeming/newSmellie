Control software for the SMELLIE optical calibration system via XMLPRC.
Documentation available on http://www-pnp.physics.ox.ac.uk/~dunger/smellie_doc/ or to build locally
`cd doc && make html`

Installation
======

Running the SMELLIE HW server requires you first:
* you install the PQ drivers - 
* clone this repository `git clone https://github.com/jackdunger/newSmellie.git`

It is assumed that you run SMELLIE in a virtual environment. If not already installed get venv with `pip install virtualenv`:
* First create the virtual env  `virtualenv venv`
* Then activate it  `source venv/bin/activate`

Then install the SMELLIE software with:
`python setup.py install`

