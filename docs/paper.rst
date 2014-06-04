.. image:: logo.png
   :align: center
   :target: index.html

|

=======================================================
Design and implementation of the APRS Messaging Service
=======================================================

| *Antony Chazapis, SV1OAN*
| *chazapis@gmail.com*

*Version 0.1, May 2014*

Summary
-------

The *APRS Messaging Service* provides a familiar, email interface to APRS messaging, making it compatible with existing email client software and services. It is built upon the APRS-IS, and utilizes common protocols like IMAP and SMTP. APRS-MS is open source and a running instance is available at ``aprs-ms.net``.

Introduction
------------

The `Automatic Packet Reporting System <http://www.aprs.org/>`_ is a digital communications protocol used by radio amateurs, to collaboratively update a map, exchange text messages, and share other information. Its usage is wide-spread and many modern transceivers offer embedded APRS functionality without the need of extra equipment.

APRS is a protocol, defining the method of communication between parties. Higher-level services may provide additional operations, on top of the underlying communications channel.

`APRS-IS <http://www.aprs-is.net>`_, the *APRS Internet Service* is one such service. It collects all APRS on-air traffic and forwards it throughout a distributed network of online servers. Thus, a radio amateur can follow APRS information without a radio, for any place around the world. The `Google Maps APRS <http://aprs.fi/>`_ service builds upon APRS-IS to provide a global, live picture of APRS objects on a map. The Google Maps APRS project has succeeded into bridging APRS technology with the contemporary Internet, and presenting a vast amount of information through a well-known and user-friendly interface.

But APRS is not just about the map. It is also about messaging. To take APRS messaging to the next level, we need a service that will extend the current functionality and transform the usage pattern closer to modern Internet practice.

The *APRS Messaging Service* aims to be to APRS what the email server is to `SMTP <http://en.wikipedia.org/wiki/Simple_Mail_Transfer_Protocol>`_. It stores all exchanged messages and makes them accessible through the common software interface supported by all email clients - `IMAP <http://en.wikipedia.org/wiki/Internet_Message_Access_Protocol>`_.

Thus, a message sent to an offline user is no longer ignored. The recipient can check received messages at a later time, using any kind of device that runs an email client software. The email software may also implement additional features, such as periodically checking for new messages, automatically replying, forwarding received messages to some other email address or group, etc. The simple idea of applying the email paradigm to APRS messages allows for unconditional reuse of existing email software and related tools for APRS messaging.

APRS-MS should be useful in a multitude of scenarios, ranging from casual messaging to amateur radio emergency service. It effectively unifies the APRS messaging and email technologies. An operator can send an email to multiple recipients and expect that it will reach them on their computers and mobile phones, as well as their radios, if there is an IGate in the area. During marathon run communications, all radio amateurs may send information to the operations center, using either their APRS-enabled radios or their mobile phones - depending on mobile network data coverage and available equipment.

Technical details
-----------------

APRS-MS runs on top of APRS-IS. The APRS-MS server connects to an APRS-IS server and receives all messaging traffic. Some APRS-IS servers provide a special port for such data, but messages can also be selected with the appropriate ``filter`` command.

All messages are parsed and stored in a database, by the *collector* process. For each message, we store the ``sender``, the ``recipient``, the ``body``, the ``timestamp`` and a ``read`` flag, which indicates if the message has been read by the recipient.

Clients connect to the *IMAP* service to receive messages, which speaks the corresponding protocol. The service uses the login username as the callsign to populate the *Inbox* and *Sent* folders from the messages, by matching the recipient and sender respectively. The contents of both folders can not be changed - no messages can be moved or deleted. The only allowed operation is to change a message's ``read`` status.

To format an APRS message as an email, APRS-MS sets the sender and recipient fields to a virtual email address consisting of the callsign and the APRS-MS server's domain. For example, sender ``SV1OAN-7`` will be converted to ``SV1OAN-7 <SV1OAN-7@aprs-ms.net>``. The message body is shown as both the email's subject and body. Initially, the message body was only copied to the email's body. However, emails with empty subjects are not shown nicely in most email client software.

To send a message, the email software connects to the *SMTP* service. This service does not use the database, but rather reformats the incoming message to be APRS-compatible and submits it to the APRS-IS service. The subject and body of the email are concatenated and the resulting string truncated to 67 characters, to meet the APRS message length restriction. In this way, the sender can choose to put the APRS message text in either the subject or the body of the email. Care must be taken not to leave the default texts untouched when hitting *reply* to an email from APRS-MS. Also, note that messages travelling in the APRS-IS network will not reach RF if there is no local IGate forwarding APRS-IS traffic to RF.

The APRS-MS code is written in the `Python <https://www.python.org/>`_ programming language, using the `Twisted <https://twistedmatrix.com/trac/>`_ networking library. The project is open source, with all resources available at `GitHub <https://github.com/chazapis/APRS-MS>`_. This includes the code, installation instructions, and all documentation.

The project is currently in an early alpha stage, looking for contributions from developers and feedback from testers.
