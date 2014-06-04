#!/bin/bash

# Installation of the aprs-ms.net server.
# Tested on Ubuntu 14.04 64-bit.

apt-get install -y postgresql-9.3
sed -i 's/^\(local[ ]\+all[ ]\+all[ ]\+\)peer$/\1trust/g' /etc/postgresql/9.3/main/pg_hba.conf
service postgresql restart
su - postgres -c 'createuser -D -A -R aprs-ms'
su - postgres -c 'createdb -O aprs-ms aprs-ms'

apt-get install -y python-sqlalchemy python-psycopg2 python-twisted python-setuptools
python setup.py develop

apt-get install -y supervisor
cp aprs-ms.etc /etc/aprs-ms.cfg
cp aprs-ms-collect.supervisor /etc/supervisor/conf.d/aprs-ms-collect.conf
cp aprs-ms-imap.supervisor /etc/supervisor/conf.d/aprs-ms-imap.conf
supervisorctl reload

apt-get install -y python-docutils
( cd ../docs && for i in `ls *.rst`; do rst2html --stylesheet=rst2html.css --link-stylesheet ${i} ${i%.*}.html; done )

apt-get install -y nginx-light
sed -i 's/\# server_names_hash_bucket_size/server_names_hash_bucket_size/g' /etc/nginx/nginx.conf
cp aprs-ms.nginx /etc/nginx/sites-available/aprs-ms
( cd /etc/nginx/sites-enabled && ln -s /etc/nginx/sites-available/aprs-ms )
service nginx restart

apt-get install -y bind9
cp aprs-ms.bind /etc/bind/db.aprs-ms.net
echo $'\nzone "aprs-ms.net" { type master; file "/etc/bind/db.aprs-ms.net"; };' >> /etc/bind/named.conf.local
