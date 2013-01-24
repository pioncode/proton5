#!/usr/bin/perl 
# CGI script to generate RSS XML feed for latest issue. 
# Usage: .../xml.cgi?journal=P
# more efficient to run from the command line daily (static file,no SQL overhead):
#  rss.cgi journal=P|tail +3 > p_rss.xml

use DBI;
use CGI qw(:standard);

#print header;

print "Content-type: application/xml\n\n";
$journal=secure(param('journal'));


if ($journal eq 'P'){
  $jname='Perception'; $issn="0301-0066", $eissn="1468-4233"; $jurl="http://www.perceptionweb.com";
  $website='www.perceptionweb.com';
} elsif ($journal eq 'A'){
  $jname='Environment and Planning A'; $issn="0308-518X", $eissn="1472-3409"; $jurl="http://www.envplan.com/epa";
  $website='www.envplan.com'
} elsif ($journal eq 'B'){
  $jname='Environment and Planning B'; $issn="0265-8135", $eissn="1472-3417"; $jurl="http://www.envplan.com/epb";
  $website='www.envplan.com'
} elsif ($journal eq 'C'){
  $jname='Environment and Planning C'; $issn="0263-774X", $eissn="1472-3425"; $jurl="http://www.envplan.com/epc";
  $website='www.envplan.com'
} elsif ($journal eq 'D'){
  $jname='Environment and Planning D'; $issn="0263-7758", $eissn="1472-3433"; $jurl="http://www.envplan.com/epd";
  $website='www.envplan.com'
} elsif ($journal eq 'I'){
  $jname='i-Perception'; $issn="2041-6695", $eissn="2041-6695"; $jurl="http://i-perception.perceptionweb.com";
  $website='i-perception.perceptionweb.com'
} else {
  die "ERROR!!";
}
  






$dbh = DBI->connect("dbi:Pg:dbname=journals;host=localhost;port=5432", "jon", "")||die "couldn't connect";

# Determine the latest issue
#$findlastvol=$dbh->prepare("select max(volume), max(issue) from issues where journal='$journal' and online=1;") || die;

#$findlastvol=$dbh->prepare("select volume, max(issue) from issues where journal='$journal' and volume=(select max(volume) from issues where journal='$journal' and online=1) and online=1 group by volume order by volume desc;") || die;

$findlastvol=$dbh->prepare("select volume, max(issue) from papers where journal='$journal'  group by volume order by volume desc;") || die;

$findlastvol->execute()||die "Can't execute query\n";
($maxvol, $maxiss)=$findlastvol->fetchrow();

# get the contents
$sth=$dbh->prepare("select title, issue, start_page, end_page, abstract, paperid, ptype from papers where journal='$journal' and (volume=$maxvol and issue=$maxiss or start_page=0) order by start_page;") || die;

$sth->execute()||die "Cannot execute query\n";

#print the preamble
#<?xml version="1.0" encoding="ISO-8859-1"?>
print <<END;
<?xml version="1.0" encoding="utf-8"?>

<rdf:RDF
 xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
 xmlns="http://purl.org/rss/1.0/"
 xmlns:taxo="http://purl.org/rss/1.0/modules/taxonomy/"
 xmlns:dc="http://purl.org/dc/elements/1.1/"
 xmlns:syn="http://purl.org/rss/1.0/modules/syndication/"
 xmlns:prism="http://purl.org/rss/1.0/modules/prism/"
 xmlns:admin="http://webns.net/mvcb/"
>

<channel rdf:about="http://www.pion.co.uk">
<title>$jname</title>
<link>$jurl</link>
<description>$jname volume $maxvol issue $maxiss</description>
<prism:eIssn>$eissn</prism:eIssn>
<prism:coverDisplayDate></prism:coverDisplayDate>
<prism:publicationName>$jname</prism:publicationName>
<prism:issn>$issn</prism:issn>
END

print "<items>\n";
print " <rdf:Seq>\n";
while (@result=$sth->fetchrow()){
  ($title, $issue, $start_page, $end_page, $abstract, $paperid, $ptype)=@result;
   $paperid =~ s/\s*$//;  # remove trailing spaces
#  if ($journal eq 'I'){
    print "  <rdf:li rdf:resource=\"http://$website/journal/I/article/$paperid\" />\n";
#  } else {
#    print "  <rdf:li rdf:resource=\"http://$website/abstract.cgi?id=$paperid\" />\n";
#  }
} 

print " </rdf:Seq>\n</items>\n</channel>"; 
 
#rewind  fetchrow cursor..... TODO!
$sth->execute()||die "Cannot execute query\n";  #waste of time!


while (@result=$sth->fetchrow()){
  ($title, $issue, $start_page, $end_page, $abstract, $paperid, $ptype)=@result;
  $paperid =~ s/\s*$//;  # remove trailing spaces  
  #get the authors
  $authquery=$dbh->prepare("select first_name, last_name from authors where paperid='$paperid' order by position")||die;
  $authquery->execute()||die;
  $authors="";
  while (@author=$authquery->fetchrow()){
    ($first_name,$last_name)=@author;
    $authors .= "$first_name $last_name, ";
  }
  $authors =~ s/, $//;   # remove final comma space
  #print "$authors<br>\n";
  
  # generate XML for this article
  print <<END;  
<item rdf:about="http://$website/journal/I/article/$paperid">
<title><![CDATA[$title. $authors]]></title>
<link>http://$website/journal/I/article/$paperid</link>
<description><![CDATA[$abstract
]]></description>
<dc:creator>Pion</dc:creator>

<dc:identifier>info:doi/10.1069/$paperid</dc:identifier>
<dc:title><![CDATA[$title]]></dc:title>
<dc:publisher>Pion Ltd</dc:publisher>
<prism:number>$issue</prism:number>
<prism:volume>$maxvol</prism:volume>
<prism:endingPage>$end_page</prism:endingPage>
<prism:publicationDate></prism:publicationDate>
<prism:startingPage>$start_page</prism:startingPage>
</item>
END
}
# temporarily removed:   <dc:date></dc:date>
print "</rdf:RDF>";

sub secure{
  #return only a single block of alphanumerics to prevent SQL hacking, etc 
  my $input=$_[0];
  $input=~s/\W//g; # delete any non-alpha chars
  return $input;
}