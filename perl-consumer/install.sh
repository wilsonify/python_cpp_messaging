# based on Perl code from RabbitMQ tutorials

#Here you can find Perl code examples from [RabbitMQ
#tutorials](https://www.rabbitmq.com/getstarted.html).

# To successfully use the examples you will need a running RabbitMQ server.

## Requirements

# To run this code you need to install Net::RabbitFoot.
# cpan -i Net::RabbitFoot

# For tutorial six UUID::Tiny needs to be installed.
# cpan -i UUID::Tiny

# There are known problems with the the Net::RabbitFoot module:

# * The MooseX::AttributeHelpers dependency has been deprecated and no longer builds on Perl 5.18
# * The library tests fail on 32bit systems

# On Ubuntu:

sudo apt-get install make libclass-data-inheritable-perl libtest-deep-perl libmoosex-app-cmd-perl libcoro-perl libjson-xs-perl libxml-libxml-perl libconfig-any-perl libmoosex-attributehelpers-perl libmoosex-configfromfile-perl libtest-exception-perl libfile-sharedir-perl libreadonly-xs-perl libuuid-tiny-perl
sudo cpan -i Net::RabbitFoot
