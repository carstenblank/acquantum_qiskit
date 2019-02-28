acquantum-qiskit
################

.. image:: https://img.shields.io/readthedocs/acquantum_qiskit.svg?style=for-the-badge
    :target: https://acquantum_qiskit.readthedocs.io/en/latest/?badge=latest
    :alt: Read the Docs

.. image:: https://img.shields.io/travis/com/carstenblank/acquantum_qiskit.svg?style=for-the-badge
    :target: https://travis-ci.com/carstenblank/acquantum_qiskit
    :alt: Travis Build

.. image:: https://img.shields.io/codacy/grade/83e6c1a12f7942998cbbeb3d34f08964.svg?style=for-the-badge
    :target: https://www.codacy.com?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=sebboer/acquantum_qiskit&amp;utm_campaign=Badge_Grade
    :alt: Codacy

.. image:: https://img.shields.io/pypi/v/acquantum_qiskit.svg?style=for-the-badge
    :alt: PyPI
    :target: https://pypi.org/project/acquantum-connector

.. image:: https://img.shields.io/pypi/pyversions/acquantum_qiskit.svg?style=for-the-badge
    :alt: PyPI - Python Version
    :target: https://pypi.org/project/acquantum-connector

A qiskit provider for the Alibaba's quantum computer.

Installation
============

This plugin requires Python version 3.5 and above, as well as qiskit.
Installation can be done using pip:

Install from PyPI
-----------------

.. code-block:: bash

    $ pip install acquantum-qiskit


.. getting-started-start-inclusion-marker-do-not-remove

Getting started
===============

As this provider is only needed to actually run a quantum circuit, pretty much the whole stack
is identical as already known. The only difference is that the provider must be instantiated
explicitly and the credentials must be given: either directly through user/password or by
setting system environment variables `ACQ_USER` and `ACQ_PWD`.

.. code-block:: python

    import qiskit
    import qiskit.extensions.standard as standard
    from qiskit.circuit.measure import measure
    from qiskit.circuit import QuantumCircuit, QuantumRegister, ClassicalRegister

    from acquantum_qiskit import AcQuantumProvider

    q = QuantumRegister(2, "q")
    r = QuantumRegister(1, "r")
    c = ClassicalRegister(2, "c")
    ca = ClassicalRegister(1, "c^a")
    qc = QuantumCircuit(q, r, c, ca, name="TestCircuit")
    standard.h(qc, q[0])
    standard.cx(qc, q[0], q[1])
    standard.x(qc, r)
    measure(qc, q, c)
    measure(qc, r, ca)

    # Create the provider
    provider = AcQuantumProvider()

    # load_account without arguments tries to load from system environment varables
    # the user (ACQ_USER) and password (ACQ_PWD)
    provider.enable_account()

    # if this is not what you want instantiate instead
    # ===> uncomment this if you want this:
    # provider.enable_account(user='your_user', password='xxxxxxxx')

    backend = provider.get_backend("SIMULATE")  # type: AcQuantumBackend

    # Execute and print out the results
    job = qiskit.execute(qc, backend, shots=1024, seed=None)
    result = job.result()
    print(result.get_counts())


.. getting-started-end-inclusion-marker-do-not-remove

Contributing
============

We welcome contributions - simply fork the repository of this plugin, and then make a
`pull request <https://help.github.com/articles/about-pull-requests/>`_ containing your contribution.
All contributers to this plugin will be listed as authors on the releases.

We also encourage bug reports, suggestions for new features and enhancements, and even links to cool projects or applications built on this project.

License
=======

The AcQuantum Qiskit Provider is **free** and **open source**, released under
the `Apache License, Version 2.0 <https://www.apache.org/licenses/LICENSE-2.0>`_.

.. license-end-inclusion-marker-do-not-remove
