#!/usr/bin/perl -T
# email alert service: process activation

%jname= (
 "I" => "i-Perception",
 "A" => "Environment and Planning A",
 "B" => "Environment and Planning B: Planning and Design",
 "C" => "Environment and Planning C: Government and Policy",
 "D" => "Environment and Planning D: Society and Space"
);

%jname= (
 "I" => "i-Perception",
 "A" => "Environment and Planning A",
 "B" => "Environment and Planning B: Planning and Design",
 "C" => "Environment and Planning C: Government and Policy",
 "D" => "Environment and Planning D: Society and Space"
);

%bannername= (
 "P" => "p_ban2.gif",
 "A" => "a_ban.gif",
 "B" => "b_ban.gif",
 "C" => "c_ban.gif",
 "D" => "d_ban.gif"
);

use CGI::Pretty qw/:standard/;
use DBI;

@weekDays = qw(Sun Mon Tue Wed Thu Fri Sat Sun);
($second, $minute, $hour, $dayOfMonth, $month, $yearOffset, $dayOfWeek, $dayOfYear, $daylightSavings) = localtime();
$thisyear = 1900 + $yearOffset;
$month++;

$db= DBI->connect("dbi:Pg:dbname=emailalert;host=localhost;port=5432", "jon", "") || failmsg("We're sorry, an error has occurred, please try again later");

$id=param('i');
$number=param('n');

# trap any non-numeric input (prevent SQL hacking)
exit unless ($id =~ /^\d+$/ && $number =~ /^\d+$/);

unless ($journal eq 'I') {
#print header, start_html(-title=>"Pion email alerting service", -style=>'pion.css', -dtd=>'-//W3C//DTD HTML 4.0 Transitional//EN');
}

$sth=$db->prepare("select random, journal, email from emailaddresses where id=$id");
$sth->execute();
($random,  $journal, $email)=$sth->fetchrow();
$journal =~s/\s*//g;

if($journal eq 'P'){
} else {
print "Expires: Thu, 01 Jan 1970 00:10:00 GMT\n"; # keep this! it stops server from caching data
print "Date:  Tues, 16 Dec 2008 00:10:00 GMT\n"; # this needs attention - we want to print current time and date
print "Content-Type: text/html; charset=utf-8\n";
print "\n";

print <<END;
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en" dir="ltr">
  <head>
<script type="text/javascript">
var timer;
function scrolltop()
{
document.getElementById('scrollmenu').style.top=document.body.scrollTop;
timer=setTimeout("scrolltop()",1);
}
function stoptimer()
{
clearTimeout(timer);
}
</script>

  <title>iPerception home page</title>
  <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
  <!--<link rel="alternate" type="application/rss+xml" title="PiMMS-development RSS" href="http://proton4/drupal-6.6/?q=rss.xml" />-->
  <link rel="shortcut icon" href="../ep/favicon.ico" type="image/x-icon" />
  <!--<link type="text/css" rel="stylesheet" media="all" href="/drupal-6.6/modules/node/node.css?N" />-->

  <link type="text/css" rel="stylesheet" media="all" href="Stylesheets-old/defaults.css?N" /> <!-- takes care of clearing floats -->
  <!--<link type="text/css" rel="stylesheet" media="all" href="/drupal-6.6/modules/system/system.css?N" />-->
  <link type="text/css" rel="stylesheet" media="all" href="Stylesheets-old/system-menus.css?N" /><!-- affects colours of active menu links -->
  <!--<link type="text/css" rel="stylesheet" media="all" href="/drupal-6.6/modules/user/user.css?N" />-->
	    <link type="text/css" rel="stylesheet" media="all" href="Stylesheets-old/styleip.css" /> <!-- takes care of main style issues -->
<!--<link type="text/css" rel="stylesheet" media="all" href="/drupal-6.6/themes/garland/minnelli/minnelli.css?N" />-->
	      <link type="text/css" rel="stylesheet" media="print" href="Stylesheets-old/print.css?N" /> 
	      <!-- I haven\'t looked into how this works, but generates print content that skips the graphicals sidebars and header - just reproducing contents of center box -->
  <!--[if lt IE 7]>
  <link type="text/css" rel="stylesheet" media="all" href="/drupal-6.6/themes/garland/fix-ie.css" />    <![endif]-->

  </head>
  <body onload="scrolltop()" onunload="stoptime()" class="sidebars"> <!-- without this everything would be left-aligned -->
  <!-- Layout -->
  <!-- NOTE: the css file has "descendent selectors", ie nested divs, so removing one div changes style of another! -->
  <!-- therefore, a "header" in a "wrapper" has a different style to a "header" on its own -->
  <div id="header-region"></div><!-- puts a space at top -->
  <div id="wrapper"> <!-- Wrapper is overall area containing everything else -->
  <div id="container" class="clear-block"> <!-- container is subarea of wrapper which doesn\'t include dead space on left and right. -->

	<!--"clear-block" makes block clear float -->
	<div id="header"> <!-- this is just bit at top centre containing title (and links if used) -->

            <div class="lefty">
	    <!--<h1><a href="newcontents.cgi?journal=I" title=""><span><img src="../neil/Images/test_perception.gif" align=right border=2> </span> <font size=+1><b>&#8212; the <b>open access</b> journal of human, animal, and machine perception</b></font></a></h1>-->
<a href="newcontents.cgi?journal=I" title=""><img class="bannerfloat2" src="Images/ip-banner-white2.png" height=96 align=right border=2></a><h1><span><a href="newcontents.cgi?journal=I" title=""></span> <font size=+1><b>&#8212; the <b>open access</b> journal of human, animal, and machine perception</b></font></a></h1>	    <!--<h1><a href="newcontents.cgi?journal=I" title=""><img class="headericon" src="Images/b_ban3.gif"><span></span> <font size=+1>&#8212; the <b>open access</b> journal of human, animal, and machine perception</font></a></h1>-->

            </div>

	  <div id="logo-floater">
	  </div>
        </div>
<div id="sidebar-left" class="sidebar">
  <div id="block-user-1" class="clear-block block block-user"> <!-- not sure what user bit does (nothing on layout?), block (with content) has small margin -->
    <h2></h2>
      <div class="content"> <!-- descendent on block class, this puts in a small margin, doesn\'t seem to do much else -->

        <ul class="menu">
<p><a href="iperception.cgi" title="i-Perception"><div class="clear-block"><img class="thinborderfloat" src="Images/ipcover3.png" align=right border=2 height=365 width=256></a></ul>
</div>
</div>
</div>
        <div id="center"> <!-- the following divs are all descendent -->
	  <div id="squeeze">
	    <div class="right-corner">
	      <div class="left-corner">
		<div class="clear-block">

		  <div id="node-5" class="node"> <!-- this puts a line under the text (same colour as background), giving the impression that the block is separated in two-->
    
				<div class="clear-block">
				    
				    <h4><i>i-Perception</i> alerting service</font> <div id="issn">ISSN 2041-6695 (online)</h4>
				    </div> 
END
}

$footer=<<END;
</div>
                <i></i> &copy; $thisyear Pion Ltd.
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
</body>
</html>
END

if ($random == $number){
  $db->do("update emailaddresses set confirmed=true where id=$id") || failmsg("We're sorry, an error has occurred, please try again later");
  
  # delete any other rows containing this email address
  $db->do("delete from emailaddresses where email='$email' and journal='$journal' and confirmed is false");
  
  print p, "Thank you for registering for the email alerting service.  You will receive an email alert when there is any significant news relating to <i>$jname{$journal}</i> or when new content is added to <a href='http://www.i-perception.info'>http://www.i-perception.info</a>.", p, "Click <a href='http://www.i-perception.info'>here</a> to go to the journal homepage. <p>If you wish to unsubscribe from the alerting service, please click <a href='unsubscribe.cgi?i=$id&amp;n=$random'>here</a>.";
} else {
  unless ($random){print p, "You have already unsubscribed from this service."}
  else {print p, "Invalid input"}
}

print $footer, end_html;

sub failmsg {
  print p, $_[0];
  exit;
}
