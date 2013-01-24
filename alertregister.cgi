#!/usr/bin/perl -T
# collect email address. If entry not in database, send confirmation email with random number (stored in DB) which contains link to confirm.cgi?id=xx&conf=random_number. Confirm.cgi checks that numbers match, then sets active flag in DB (DB to be dumped and rsync'd to proton4). Another script, remove.cgi?id=xx&conf=random_number deletes row (user is prompted whether to continue and script calls itself with remove.cgi?id=xx&conf=random_number&ok=y)
# If email is already in database, and new journal or warn, as appropriate.
# Each journal needs a separate service.

# create cronjob to delete from emailaddresses where now()-regdate>'2 weeks' and confirmed is false 

$TESTMODE=1;  # disable captch check for testing on proton4 - set to 0 for normal operation!!!

use CGI::Pretty qw/:standard/;
use Mail::SendEasy;
use DBI;
use Captcha::reCAPTCHA;

my $c = Captcha::reCAPTCHA->new unless $TESTMODE;

$db= DBI->connect("dbi:Pg:dbname=emailalert;host=localhost;port=5432", "jon", "") || die;

$email=param('email');
$emailconf=param('emailconf');
$journal=param('journal');
$challenge=param('recaptcha_challenge_field');
$response=param('recaptcha_response_field');

$host=$ENV{'HTTP_HOST'};

@weekDays = qw(Sun Mon Tue Wed Thu Fri Sat Sun);
($second, $minute, $hour, $dayOfMonth, $month, $yearOffset, $dayOfWeek, $dayOfYear, $daylightSavings) = localtime();
$thisyear = 1900 + $yearOffset;
$month++;

%baseurl= (
 "P" => "www.perceptionweb.com", 
 "I" => "www.perceptionweb.com/i-perception/",
 "A" => "www.envplan.com",
 "B" => "www.envplan.com",
 "C" => "www.envplan.com",
 "D" => "www.envplan.com"
);

%jname= (
 "P" => "Perception",
 "A" => "Environment and Planning A",
 "B" => "Environment and Planning B: Planning and Design",
 "C" => "Environment and Planning C: Government and Policy",
 "D" => "Environment and Planning D: Society and Space",
 "I" => "i-Perception"
);

%bannername= (
 "P" => "p_ban2.gif",
 "A" => "a_ban.gif",
 "B" => "b_ban.gif",
 "C" => "c_ban.gif",
 "D" => "d_ban.gif",
    "I" => "i_ban.gif"
);

exit unless $journal eq 'A' || $journal eq 'B' || $journal eq 'C' || $journal eq 'D' || $journal eq 'P' || $journal eq 'I';

# TODO: add captcha

if ($journal eq 'P'){$pubkey='6LcpxwAAAAAAALvPghTLwcJWGU-edxKrGJa5bi58'; $privkey='6LcpxwAAAAAAAJ7jokS9Hq32l28nzcRirNUFK2G5'}
elsif($journal=~/[A-D]/){
  $pubkey='6LfkxgAAAAAAALou3A9QZAMTKvqwjdAfFiaX4ijj'; $privkey='6LfkxgAAAAAAAH21msYa6CRw1tT07aul4FQ0W8ut'
}
elsif($journal eq 'H'){$pubkey='6LflxgAAAAAAAEpO12uWfXd52VBJg1yMH-nMbX0N'; $privkey='6LflxgAAAAAAAK8I2lxGnx3JEc-VNBYQw5p0-qrw'}
else {$pubkey='6LfixgAAAAAAAELRcfnOLvvA6_5IT2Xk5KAxIEmD'; $privkey='6LfixgAAAAAAAFsqiAYC1ftt-HatJ0WWnZVgov_O'}

$captcha=$c->get_html( $pubkey, $err, $ssl, ('theme'=>'white') ) unless $TESTMODE;

my $result = $c->check_answer(
        $privkey, $ENV{'REMOTE_ADDR'},
        $challenge, $response
    ) unless $TESTMODE;
    
$valid_captcha= $result->{is_valid} unless $TESTMODE;

$valid_captcha=1 if $TESTMODE;

$email=~s/\s//g;   # clean this up to prevent SQL hacking
$emailconf=~s/\s//g;

# TODO: If not a valid Pion hostname (eg connecting via a proxy), redirect user to direct site.

unless ($journal eq 'I') {
    print header, start_html(-title=>"Pion email alerting service", -style=>'pion.css', -dtd=>'-//W3C//DTD HTML 4.0 Transitional//EN');
}

if($journal eq 'P'){
} elsif ($journal eq 'I') {
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
				    
				    <h4>Register for the <i>i-Perception</i> alerting service</h4> <div id="issn">ISSN 2041-6695 (online)</div>
				    </div> 
END


} elsif($journal eq 'X'| $journal eq 'E'| $journal eq 'A'| $journal eq 'B'| $journal eq 'C'| $journal eq 'D') {
} else {
print <<END;
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

if ($email eq $emailconf && $email=~/.+@.+?\.\w+$/ && $valid_captcha){
  #
  #print p, "[addresses match and have the right form, valid captcha]";
  
  $mail = new Mail::SendEasy(smtp => 'mailgate.pion.ltd.uk');
  
  #$email='jon@pion.co.uk'; #override real email for testing purposes
  # generate random number $random, get next id from db, insert all into database 
  
  # check if already subscribed
  $sth=$db->prepare("select id, random from emailaddresses where email='$email' and journal='$journal' and confirmed is true;");
  $sth->execute();
  ($old_id, $old_random)=$sth->fetchrow();
  
  if ($old_id){
    print p, "You are already subscribed to email alerting for $jname{$journal}. You will receive an email alert when there is any significant news relating to <i>$jname{$journal}</i> or if new content is available. No further action is required. <p> Click <a href='http://www.i-perception.info'>here</a> to go to the journal homepage. <p>If you wish to unsubscribe from the alerting service, please click <a href='unsubscribe.cgi?i=$old_id&amp;n=$old_random'>here</a>.", $footer, end_html;
    exit;
  }
  
  $sth=$db->prepare("select count(*) from emailaddresses where email='$email' and journal='$journal' and confirmed is false and now()-regdate<'3 minutes';");
  $sth->execute();
  ($registered)=$sth->fetchrow(); 
  
  if ($registered>0){
    print p, "You have already registered for email alerting to <i>$jname{$journal}</i>, and an activation email was sent to your address. Please click the link in the email we sent to activate the alerting service. If you do not recall receiving the activation email, please check carefully if the message has been identified as spam by your spam filters. If the activation email was identified as spam, please ensure that any spam filtering on your system is set to accept email from pion.co.uk, so that the notification emails will not also be identified as spam. <p>Click <a href='http://www.i-perception.info'>here</a> to go to the <i>$jname{$journal}</i> homepage.", $footer, end_html;
    exit;
  }
  
  $sth=$db->prepare("select nextval('id_seq')");
  $sth->execute();
  ($id)=$sth->fetchrow();
  
  $random=int(rand(1000000));
  
  $email_q=$db->quote($email);
   
  $db->do("insert into emailaddresses values ($id, $email_q, '$journal', $random, now(), false)"); 
  #print "insert into emailaddresses values ($id, $email_q, '$journal', $random, now, false)" ;
  $status = $mail->send(
         from    => 'alerts@pion.co.uk' ,
         from_title => 'Pion email alerting service',
         to      => $email ,
         subject => "$jname{$journal} email alerting activation" ,
         msg     => "Thank you for signing up to the email alerting service for $jname{$journal}.\n\nIn order to activate the service, please click on the following link:\n\nhttp://i-perception.perceptionweb.com/emailconfirm.cgi?i=$id&n=$random\n\nYou will be able to unsubscribe at any point simply by clicking on the \"unsubscribe\" link which can be found in the alert emails.\n\n\nPlease do not reply to this message.\n"
         )  ;
         print "Problem sending message" if($mail->error); 
  print p, "An email message has now been sent to your address. Please open the message and click on the link to activate the email alerting service for <i>$jname{$journal}</i>. If you have not received this message within three minutes please check if the message has been identified as spam by your spam filters. If the activation email was identified as spam, please ensure that any spam filtering on your system is set to accept email from pion.co.uk, so that the notification emails will not also be identified as spam.
<p> Click <a href='http://www.i-perception.info'>here</a> to go to the <i>i-Perception</i> homepage.", $footer, end_html;  
} else {
  $errormsg="<font color='red'>The email addresses entered do not match or are invalid. </font>" unless $email eq $emailconf;
  $errormsg .= "<font color='red'><br>The verification words were not recognised - please try again.</font>" unless $valid_captcha || !$email;
  printform($errormsg);
}

sub printform {
  #if ($host !~ /envplan.com$/ && $host !~ /perceptionweb.com$/ && $host !~ /hthpweb.com$/){
   # print p, "The registration page you are trying to access will not operate correctly via a proxy address, which you appear to be using (for example, you might have accessed the $baseurl{$journal} pages via a university login). In order to register for email alerts, please copy and paste the following address into your web browser and complete the instructions therein: <p>http://$baseurl{$journal}/alertregister.cgi?journal=$journal <p>Once you have completed the registration process, you can continue to access $baseurl{$journal} pages via your proxy address."
  #} 
  #else {
     $captcha_blurb='and enter the two security words into the dialog box provided. (Note: the security words are not case sensistive, and a facility exists to generate new words if the those currently displayed are difficult to read; an audio security feature is also available, for the visually impaired. These features are accessed via the red buttons to the right of the dialog box)' unless $TESTMODE;
    print "<p>If you would like to be kept informed regarding the latest developments with <i>i-Perception</i>, and to be notified when the first and subsequent issues of the journal are published, please enter and confirm your email address in the boxes provided below$captcha_blurb. 
  <p>Your email will not be divulged to any third parties and will only be used to send occasional alerts relating to <i>i-Perception</i> developments or new content. You can unsubscribe at any point by clicking on the link provided in the alert emails.<br>";
    if ($journal eq 'X'| $journal eq 'E'| $journal eq 'A'| $journal eq 'B'| $journal eq 'C'| $journal eq 'D') {
      print "<p>Please note that an identical service is offered by each of the <i>Environment and Planning</i> journals; to subscribe to the alerting service for another <i>E&P</i> journal please visit the journal homepage from the links above.<br>";
    }
    print  $_[0], p,
      start_form, "Enter email address: <br>", textfield(-name=>'email', -size=>50),
      br, "Confirm email address: <br>", textfield(-name=>'emailconf', -size=>50), "<input type=hidden name = journal value =$journal>", br
      br, $captcha, br, p, "<b>Note: Before clicking Submit, please ensure that any spam filtering on your system is set to accept email from pion.co.uk.</b>",
      p, submit(-name=>'Submit'), end_form, $footer, end_html;
   #} 
    exit;
}
