#!/bin/sh

NAGIOS_NAME=nagios-4.0.8
PLUGIN_NAME=nagios-plugins-2.0

cd $NAGIOS_NAME
./configure --with-command-group=nagcmd
make all
make install
make install-init
make install-config
make install-commandmode
make install-webconf

cp -R contrib/eventhandlers/ /usr/local/nagios/libexec/
chown -R nagios:nagios /usr/local/nagios/libexec/eventhandlers

/usr/local/nagios/bin/nagios -v /usr/local/nagios/etc/nagios.cfg
/etc/init.d/nagios start

/etc/init.d/httpd start

cd ../$PLUGIN_NAME
./configure --with-nagios-user=nagios --with-nagios-group=nagios
make
make install

cd ../

chkconfig --add nagios
chkconfig nagios on
chkconfig --add httpd
chkconfig httpd on