#!/usr/bin/perl

use strict;
use warnings;

use FindBin '$Bin';
use lib "$Bin/lib";

use WebApp;
my $webapp = WebApp->new();
$webapp->run();
