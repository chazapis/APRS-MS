.. image:: docs/logo.png
   :align: center

|

======================
APRS Messaging Service
======================

The *APRS Messaging Service* provides a familiar, email interface to `APRS <http://www.aprs.org/>`_ messaging, making it compatible with existing email client software and services. It is built upon the `APRS-IS <http://www.aprs-is.net>`_, and utilizes common protocols like `IMAP <http://en.wikipedia.org/wiki/Internet_Message_Access_Protocol>`_ and `SMTP <http://en.wikipedia.org/wiki/Simple_Mail_Transfer_Protocol>`_. APRS-MS is open source and a running instance is available at `aprs-ms.net <http://aprs-ms.net>`_. `Read more <docs/paper.rst>`_

Installation and configuration
------------------------------

To install, run ``python setup.py install``.

You can easily test the code inside a `virtualenv <https://virtualenv.pypa.io/>`_.

After installation, you can run ``aprs-ms-collect`` to get all message traffic into the database, and ``aprs-ms-imap`` to offer IMAP connectivity. Options are set in ``aprs-ms.cfg`` files found in the folder from where the executables are run, ``/etc``, and where the ``APRS_MS_CONFIGURATION`` environmental variable points to. A sample configuration file can be found in the root of the source repository.
