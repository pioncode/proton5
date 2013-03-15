package WebApp;
use base 'CGI::Application';
#use CGI::Session;
#use CGI::Cookie;
use strict;
use warnings;
use Data::Dumper;

# needed for our database connection
use CGI::Application::Plugin::DBH qw/dbh_config dbh/;
 use CGI::Application::Plugin::Session;

# add Template Toolkit support to CGI::Application
use CGI::Application::Plugin::TT;

# add routes-style dispatchin
use CGI::Application::Plugin::Routes;

# Add CGI::Session support to CGI::Application
use CGI::Application::Plugin::Session;

# S E T U P





sub setup {
    my $self = shift;

    # define routes table
    $self->routes([
        ''                                                       => 'showlistvolumes',
        '/journals'                                              => 'showlistjournals',
        '/journal/:journal_id'                                   => 'showlistvolumes',
        '/journal/:journal_id/volumes'                           => 'showlistvolumes',
        '/journal/:journal_id/volume/:volume_id'                 => 'showlistissues',
        '/journal/:journal_id/volume/:volume_id/issue/:issue_id' => 'showlistpapers',
        '/journal/:journal_id/volume/:volume_id/article/:id'     => 'showarticle',
        '/journal/:journal_id/article/:id'                       => 'showarticle',
        '/page/:page_id'                                         => 'showstatic',
        '/faq/:id'                                               => 'showfaq',
        '/aboutcover'                                        => 'aboutcover',
        '/journal/:journal_id/searchresults'                                        => 'showsearchresults',
        '/journal/:journal_id/theme/:theme_id'                 => 'showlisttheme',
#	'/admin'					=> 'admin',
    ]);

    # define modes
    # unnecessary if use Routes
    #$self->run_modes( [qw/showstatic showarticle showlistjournals showlistvolumes showlistissues showlistpeapers/] );

    # start mode
    # the mode key specified here will be used whenever the value of the CGI form parameter specified by mode_param() is not defined
    $self->start_mode('showlistvolumes');

    # set error mode
    # if the runmode dies for whatever reason
    # run() will call that method as a run mode, passing $@ as the only parameter
    $self->error_mode( 'showerror' );

    # if CGI::Application is asked to go to a run mode which doesn't exist it will usually croak() with errors.
    # you can catch this exception by implementing a run mode with the reserved name "AUTOLOAD"
    # this run mode will in invoked just like a regular run mode, with one exception:
    # it will receive, as an argument, the name of the run mode which invoked it
    $self->run_modes( AUTOLOAD => 'showerror' );
    
    # Configure the session
    $self->session_config(
       DEFAULT_EXPIRY      => '+1h',
       COOKIE_PARAMS       => {
                                -expires => '+1h',
                                -path    => '/',
                              },
       SEND_COOKIE         => 1,
    );


    # set options for templates
    $self->tt_config( TEMPLATE_NAME_GENERATOR => \&__my_template_name );

    # connect to DBI database, with the same args as DBI->connect();
    $self->dbh_config( 'dbi:Pg:dbname=journals;host=localhost;port=5432;', 'jon', '' );
    $self->header_type('header');
    $self->header_props(     -type=> 'text/html; charset=utf-8'    );  # this allows us to keep unicode character embedded in the database


    return $self;
}

sub teardown {
    my $self = shift;

    # disconnect when we're done
    $self->dbh->disconnect();

    return $self;
}


# M O D E S

# show admin pages
#sub admin{
#my $self = shift;

## Redirect to login unless there is a login cookie or the username and passoword was retuned from the login page.
#unless ( $self->session->param('pion_login') eq 'admin' ) {

# if( ($self->query->param('username') eq 'padmin') && ($self->query->param('password') eq 'ad_p10n#') ){
##  print "Content-type: text/html\n\n";
##  print "<h1>Logging in...</h1>";

#  $self->session->param('pion_login','admin');
# }    
# return $self->tt_process({'admin_var'=>'login'});
# }

##This stuff runs if the user is logged in as admin
#if($self->session->param('pion_login') eq 'admin' ){
#  return $self->tt_process({'admin_var'=>'admin_screen'});
#}

#}



# show faq
sub showfaq {
    my $self = shift;

   # added to get contents display - jb
    my $journal_id = 'I'; # $self->query->param('journal_id');
    #                 ^ see FS#99
    my $volume_id  = int $self->query->param('volume_id');  # added JB
    # get journal and volume lists
    my $journals = $self->_get_journals;
    my $volumes  = $self->_get_volumes( $journal_id );
 #---------
    my $id   = $self->query->param('id');
    return $self->tt_process( { 'show' => $id , 'volumes'=>$volumes} );  # added volumes to get contents panel
}

# journals list
sub showlistjournals {
    my $self = shift;

    ## BLANKCOVER
    #return $self->tt_process( 'templates/blankcover.tmpl', { 'journals' => $self->_get_journals } );

    return $self->tt_process( { 'journals' => $self->_get_journals } );
}

# volumes list
sub showlistvolumes {
    my $self = shift;
    # get params from query
    my $journal_id = 'I'; # $self->query->param('journal_id');
    #                 ^ see FS#99
    my $volume_id  = int $self->query->param('volume_id');  # added JB
    # get journal and volume lists
    my $journals = $self->_get_journals;
    my $volumes  = $self->_get_volumes( $journal_id );

    # update session
    $self->session->param( 'showallvolumes', 0 );
    $self->session->param( 'showallvolumes', 1 ) if $self->query->path_info =~ /\/volumes$/xm;

    # save current
    # it is current journal and other usefull data (ex. current volumeid, issueid, etc.)
    my ($current)  = grep { $_->{'journal'} eq $journal_id } @$journals;
    $current->{'showallvolumes'} = $self->session->param( 'showallvolumes' );
    $current->{'volume_subdir'}=lc($journal_id).sprintf("%02d", $volume_id);  # pass i01 etc to construct URLs to PDF etc   -JB
    # print template

    ## BLANKCOVER
    #return $self->tt_process( 'templates/blankcover_ip.tmpl', { 'journals' => $journals, 'volumes' => $volumes, 'current' => $current } );

    return $self->tt_process( { 'journals' => $journals, 'volumes' => $volumes, 'current' => $current } );
}

# issues list
sub showlistissues {
    my $self = shift;

    # get params from query
    my $journal_id = 'I'; # (FS#99) $self->query->param('journal_id');
    my $volume_id  =  $self->query->param('volume_id');

    if ($volume_id =~ /^current$/i){    # not to be confused with $current below, which has nothing to do with current volume
      # get latest volume number
      my $volumes= $self->_get_volumes('I');
      $volume_id= $$volumes[0]->{'volume'};
    }
    else {
      $volume_id = int $volume_id;
    }

    # get journal lists
    my $journals = $self->_get_journals;

    # get all volumes (tree) from current journal
    my $volumes = $self->_get_volume_tree( $journal_id, $volume_id );

    # save current
    my ($current) = grep { $_->{'journal'} eq $journal_id } @$journals;
    $current->{'volume'} = $volume_id;
    # save year of current volume
    map { $current->{'year'} = $_->{'year'} if $_->{'volume'} == $volume_id } @$volumes;
    $current->{'showallvolumes'} = $self->session->param( 'showallvolumes' );
    $current->{'volume_subdir'}=lc($journal_id).sprintf("%02d", $volume_id);  # pass i01 etc to construct URLs to PDF etc   -JB
    # get all issues (and papers) from current volume
    my $issues = $self->_get_issues( $journal_id, $volume_id );
    $_->{'papers'} = $self->_get_papers( $journal_id, $volume_id, $_->{'issue'} ) for @$issues;

    # print template
    return $self->tt_process( { 'journals' => $journals, 'volumes' => $volumes, 'issues' => $issues, 'current' => $current } );
}

# papers list
sub showlistpapers {
    my $self = shift;

    # get params from query
    my $journal_id = 'I'; # (FS#99) $self->query->param('journal_id');
    my $volume_id  =  $self->query->param('volume_id');
    my $issue_id   =   $self->query->param('issue_id');
   
 
    
    if ($issue_id =~ /^current$/i){    # not to be confused with $current below, which has nothing to do with current volume
      # get latest volume number
      my $volumes= $self->_get_volumes('I');
      $volume_id= $$volumes[0]->{'volume'};
      #get latest issue number
      my $issues= $self->_get_issues('I', $volume_id);
      $issue_id= $$issues[-1]->{'issue'};
    }
    else {
      $volume_id = int $volume_id;
      $issue_id= int $issue_id;
 
    }
    my $issues= $self->_get_issues('I', $volume_id);  # this is a bit inefficient as the db is queried twice if issue_id=current

    # get journal lists
    my $journals = $self->_get_journals;

    # save current
    my ($current) = grep { $_->{'journal'} eq $journal_id } @$journals;
    $current->{'volume'} = $volume_id;
    $current->{'issue'}  = $issue_id;
    $current->{'issuetype'} = $$issues[$issue_id-1]->{'issuetype'};
    $current->{'heading'} =  $$issues[$issue_id-1]->{'heading'};
    $current->{'showallvolumes'} = $self->session->param( 'showallvolumes' );
    $current->{'volume_subdir'}=lc($journal_id).sprintf("%02d", $volume_id);  # pass i01 etc to construct URLs to PDF etc   -JB


    # get all volumes (tree) from current journal
    my $volumes = $self->_get_volume_tree( $journal_id, $volume_id, $issue_id );

    # gat all papers for current issue
    my ($papers) = map { $_->{papers} } grep { $_->{issue} == $issue_id } map { @{$_->{issues}} } grep { $_->{volume} == $volume_id } @$volumes;

    # print template
    return $self->tt_process( { 'journals' => $journals, 'volumes' => $volumes, 'papers' => $papers, 'current' => $current } );
}

# Theme papers list
sub showlisttheme {
     my $self = shift;

    # get params from query
    my $journal_id = 'I'; # (FS#99) $self->query->param('journal_id');
    my $theme_id  =  $self->query->param('theme_id');
    my $journals = $self->_get_journals;
    my $volumes  = $self->_get_volumes( $journal_id );
#     if ($volume_id =~ /^current$/i){    # not to be confused with $current below, which has nothing to do with current volume
#       # get latest volume number
#       my $volumes= $self->_get_volumes('I');
#       $volume_id= $$volumes[0]->{'volume'};
#     }
#     else {
#       $volume_id = int $volume_id;
#     }
  # update session
    $self->session->param( 'showallvolumes', 0 );
    $self->session->param( 'showallvolumes', 1 ) if $self->query->path_info =~ /\/volumes$/xm;

    # save current
    # it is current journal and other usefull data (ex. current volumeid, issueid, etc.)
    #my ($current)  = grep { $_->{'journal'} eq $journal_id } @$journals;
    #$current->{'showallvolumes'} = $self->session->param( 'showallvolumes' );

    # get journal lists
    my $journals = $self->_get_journals;

    # get all volumes (tree) from current journal
   # my $volumes = $self->_get_volume_tree( $journal_id, $volume_id );

    # save current
#     my ($current) = grep { $_->{'journal'} eq $journal_id } @$journals;
#     $current->{'volume'} = $volume_id;
#     # save year of current volume
#     map { $current->{'year'} = $_->{'year'} if $_->{'volume'} == $volume_id } @$volumes;
#     $current->{'showallvolumes'} = $self->session->param( 'showallvolumes' );
#     $current->{'volume_subdir'}=lc($journal_id).sprintf("%02d", $volume_id);  # pass i01 etc to construct URLs to PDF etc   -JB
#     # get all issues (and papers) from current volume
    #my $issues = $self->_get_issues( $journal_id, $volume_id );

   my ($current)  = grep { $_->{'journal'} eq $journal_id } @$journals;
   
    my $papers = $self->_get_theme_papers( $journal_id, $theme_id) ;

    # print template
    return $self->tt_process( { 'journals' => $journals,  'volumes'=>$volumes, 'papers'=>$papers, 'current'=>$current } );
}



# show article details
sub showarticle { 
    my $self = shift;

    my $volume_id  = int $self->query->param('volume_id');
    my $journal_id  = 'I'; #int $self->query->param('journal_id');   #added by jb
    # get params from query
    my $article_id = $self->query->param('id');

#     # if volume not supplied, find it
#     $volume_id = $self ->_get_volume

    # get journal lists
    my $journals = $self->_get_journals;

    # get current article
    my $article = $self->_get_article( $article_id );

    # save current
    my ($current) = grep { $_->{'journal'} eq $article->{'journal'} } @$journals;
    $current->{'volume'} = $article->{'volume'};
    $current->{'issue'}  = $article->{'issue'};
    $current->{'showallvolumes'} = $self->session->param( 'showallvolumes' );

    $current->{'volume_subdir'}=lc($journal_id).sprintf("%02d", $article->{'volume'});  # pass i01 etc to construct URLs to PDF etc   -JB

    # check (and save if exists) pdf file
    # Added mac pdf's 
    my $pdfpath = $current->{'pdfpath'}.'/'.$current->{'volume_subdir'}.'/'.$article->{'paperid'}.'.pdf';  # - corrected, JB
    my $pdf_mac_path = $current->{'pdfpath'}.'/'.$current->{'volume_subdir'}.'/'.$article->{'paperid'}.'_mac.pdf';  # - corrected, JB
    #$article->{'pdf'} = $pdf if -e ".$pdf";
    if(-e $pdfpath){                 # added by JB
      $pdfpath=~s/\/htdocs\/iperception//;   #  remove unwanted parts of path for construction of URL 
      $article->{'pdf'} = $pdfpath;
    }

    # Added mac pdf's 
    if(-e $pdf_mac_path){                 # added by RFC
      $pdf_mac_path=~s/\/htdocs\/iperception//;   #  remove unwanted parts of path for construction of URL 
      $article->{'mac_pdf'} = $pdf_mac_path;
    }

    # html file (with full text if article)
    my $html = $current->{'docpath'}.'/'.$article->{'paperid'}.'.html';
    $article->{'html'} = $html if -e ".$html";

	# check (and save if exists) icon for the article
    my $icon = $current->{'docpath'}.'/'.$article->{'paperid'}.'.png';
    $article->{'icon'} =  "/standard-icons/standard-5".'.png'; #$icon if -e ".$icon" or

    # check miscs (mark as error if not exists)
    $article->{'miscs'} = $self->_get_misc( $article->{'paperid'} );
    map { $_->{'error'} = 1 } grep { ! -e '.'.$current->{'miscpath'}.'/'.$_->{'url'} } @{ $article->{'miscs'} };

    # get all volumes (tree) from current journal
    my $volumes = $self->_get_volume_tree( $article->{'journal'}, $article->{'volume'}, $article->{'issue'} );

    # add DOI
    $article->{'doi'} = '10.1068/' . $article->{'paperid'};
    #Test if a poster exists
    my $posterpath = './posters/'.$article->{'paperid'}.'.pdf'; 
    if(-e $posterpath){                 # added by JB
      $article->{'pdf'} = 'TRUE';
    }

    # print template
    return $self->tt_process( { 'journals' => $journals, 'volumes' => $volumes, 'article' => $article, 'current' => $current } );
}

# volumes list
sub aboutcover {
    my $self = shift;

    # get params from query
    my $journal_id = 'I'; # $self->query->param('journal_id');
    #                 ^ see FS#99
    my $volume_id  = int $self->query->param('volume_id');  # added JB
    # get journal and volume lists
    my $journals = $self->_get_journals;
    my $volumes  = $self->_get_volumes( $journal_id );

    # update session
    $self->session->param( 'showallvolumes', 0 );
    $self->session->param( 'showallvolumes', 1 ) if $self->query->path_info =~ /\/volumes$/xm;

    # save current
    # it is current journal and other usefull data (ex. current volumeid, issueid, etc.)
    my ($current)  = grep { $_->{'journal'} eq $journal_id } @$journals;
    $current->{'showallvolumes'} = $self->session->param( 'showallvolumes' );
    $current->{'volume_subdir'}=lc($journal_id).sprintf("%02d", $volume_id);  # pass i01 etc to construct URLs to PDF etc   -JB
    # print template

    ## BLANKCOVER
    #return $self->tt_process( 'templates/blankcover_ip.tmpl', { 'journals' => $journals, 'volumes' => $volumes, 'current' => $current } );

    return $self->tt_process( { 'journals' => $journals, 'volumes' => $volumes, 'current' => $current } );
}

sub showsearchresults {
    my $self = shift;
    my $journal_id = 'I'; # $self->query->param('journal_id');
    return $self->tt_process();


}

# show error page
sub showerror {
    my $self       = shift;
    my $msg_error  = shift;
    my $debug_info = Dumper( $self->query );
    return $self->tt_process( { 'msg' => $msg_error, debug => $debug_info } );
}


# P R I V A T E

sub _get_journals {
    my $self = shift;
    my $sql  = 'SELECT * FROM public.journals WHERE journal = \'I\' ORDER BY journal';
                                                                        # ^ FS#99
    return $self->dbh->selectall_arrayref( $sql, { Slice => {} } ) or die "Problem with database!\n";
}

sub _get_volumes {
    my ( $self, $journal_id ) = @_;
    my $sql = 'SELECT DISTINCT( volume ), journal, year FROM public.papers WHERE journal = ? AND volume IS NOT NULL AND volume > 0 ORDER BY volume DESC';
    return $self->dbh->selectall_arrayref( $sql, { Slice => {} }, $journal_id ) or die "Problem with database!\n";
}

sub _get_issues {
    my ( $self, $journal_id, $volume_id ) = @_;
     #my $sql = 'SELECT DISTINCT( issue ), journal, volume FROM public.papers WHERE journal = ? AND volume = ? AND issue IS NOT NULL ORDER BY issue';
      my $sql = 'SELECT DISTINCT papers.issue as issue , papers.journal as journal, papers.volume as volume, issues.issuetype as issuetype, issues.heading as heading FROM papers LEFT OUTER JOIN issues ON papers.journal=issues.journal and papers.volume=issues.volume and papers.issue=issues.issue WHERE papers.journal = ? AND papers.volume = ? AND papers.issue IS NOT NULL ORDER BY papers.issue';
    return $self->dbh->selectall_arrayref( $sql, { Slice => {} }, $journal_id, $volume_id ) or die "Problem with database!\n";
}

sub _get_papers {
    my ( $self, $journal_id, $volume_id, $issue_id ) = @_;
#     my $sql = 'SELECT * FROM public.papers WHERE journal = ? AND volume = ? AND issue = ? AND paperid IS NOT NULL ORDER BY start_page';
    # new version to accomodate 'virual themes'   (jb 4/11)
    my $sql = 'SELECT *, papers.journal as journal FROM public.papers LEFT OUTER JOIN virtual_themes ON papers.virtual_theme=virtual_themes.virtual_theme_id WHERE ( (papers.journal = virtual_themes.journal) OR virtual_themes.journal IS NULL ) AND papers.journal = ? AND volume = ? AND issue = ? AND paperid IS NOT NULL ORDER BY start_page';
    my $papers = $self->dbh->selectall_arrayref( $sql, { Slice => {} }, $journal_id, $volume_id, $issue_id ) or die "Problem with database!\n";

    # fix paperid. without this paperid will be 8 chars long (database return always 8 chars, ex: 'p234    ')
    # and get authors 
    map { $_->{'paperid'} =~ s/\s+$//xm; $_->{'authors'} = $self->_get_authors( $_->{'paperid'} ) } @$papers;

    return $papers;
}


sub _get_theme_papers {
    my ( $self, $journal_id, $theme_id ) = @_;
    my $sql = 'SELECT * FROM public.papers LEFT OUTER JOIN virtual_themes ON papers.virtual_theme=virtual_themes.virtual_theme_id WHERE ( (papers.journal = virtual_themes.journal) OR virtual_themes.journal IS NULL ) AND papers.journal = ? AND virtual_theme = ? AND papers.paperid IS NOT NULL ORDER BY virtual_issue_order IS NULL, virtual_issue_order, volume, start_page';
    # new version to accomodate 'virual themes'   (jb 4/11)
    #my $sql = 'SELECT * FROM public.papers LEFT OUTER JOIN virtual_themes ON papers.virtual_theme=virtual_themes.virtual_theme_id WHERE papers.journal = ? AND volume = ? AND issue = ? AND paperid IS NOT NULL ORDER BY start_page';
    my $papers = $self->dbh->selectall_arrayref( $sql, { Slice => {} }, $journal_id, $theme_id) or die "Problem with database!\n";

    # fix paperid. without this paperid will be 8 chars long (database return always 8 chars, ex: 'p234    ')
    # and get authors 
    map { $_->{'paperid'} =~ s/\s+$//xm; $_->{'authors'} = $self->_get_authors( $_->{'paperid'} ) } @$papers;

    return $papers;
}

sub _get_article {
    my ( $self, $article_id ) = @_;
    #my $sql = 'SELECT * FROM public.papers WHERE paperid = ?';
    my $sql='SELECT *, papers.journal as journal FROM public.papers LEFT OUTER JOIN virtual_themes ON papers.virtual_theme=virtual_themes.virtual_theme_id WHERE ( (papers.journal = virtual_themes.journal) OR virtual_themes.journal IS NULL ) AND paperid = ?';
    my $article = $self->dbh->selectrow_hashref( $sql, { Slice => {} }, $article_id ) or die "Problem with database!\n";

    # fix paperid. without this paperid will be 8 chars long (database return always 8 chars, ex: 'p234    ')
    $article->{'paperid'} =~ s/\s+$//xm;

    # get authors
    $article->{'authors'}    = $self->_get_authors( $article->{'paperid'} );
    # get DOI
    my $doi_type = $self->_get_doi( $article->{'papertype'}, $article->{'paperid'} );
    # get Authors
    $article->{'authors'}    = $self->_get_authors( $article->{'paperid'} );
    

    return $article;
}

sub _get_doi {
    my ( $self, $paper_type,$paper_id ) = @_;
    my $sql = 'SELECT * FROM display_doi WHERE ptype=? || papertype=? ';
    return $self->dbh->selectall_arrayref( $sql, { Slice => {} }, $paper_id ) or die "Problem with database!\n";
}

sub _get_authors {
    my ( $self, $paper_id ) = @_;
    my $sql = 'SELECT first_name, last_name, address, email FROM public.authors LEFT JOIN public.affil USING (affilnum,paperid) WHERE public.authors.paperid = ? ORDER BY position';
    return $self->dbh->selectall_arrayref( $sql, { Slice => {} }, $paper_id ) or die "Problem with database!\n";
}

sub _get_misc {
    my ( $self, $paper_id ) = @_;
    my $sql = 'SELECT * FROM public.misc WHERE paperid = ? ORDER BY position';
    return $self->dbh->selectall_arrayref( $sql, { Slice => {} }, $paper_id ) or die "Problem with database!\n";
}

sub _get_page {
    my ( $self, $page_id ) = @_;
    my $sql = 'SELECT * FROM public.statics WHERE staticid = ?';
    return $self->dbh->selectrow_hashref( $sql, { Slice => {} }, $page_id ) or die "Problem with database!\n";
}

sub _get_volume_tree {
    my ( $self, $journal_id, $volume_id, $issue_id ) = @_;

    # get all volumes from current journal
    my $volumes = $self->_get_volumes( $journal_id );
    foreach my $volume ( @$volumes ) {
        last if not $volume_id;
        if ( $volume->{'volume'} == $volume_id ) {

            # get all issue for current volume
            $volume->{'issues'} = $self->_get_issues( $journal_id, $volume_id );

            foreach my $issue ( @{ $volume->{'issues'} } ) {
                last if not $issue_id;
                if ( $issue->{'issue'} == $issue_id ) {

                    # get all papers for current issue
                    $issue->{'papers'} = $self->_get_papers( $journal_id, $volume_id, $issue_id );
                }
            }
        }
    }

    return $volumes;
}

# return default template name for TT (templates/__mode_name__)
sub __my_template_name {
    (caller 3)[3] =~ /([^:]+)$/;
    my $name = $1;
    return 'templates/'.$name.'.tmpl';
}


1;  # Perl requires this at the end of all modules
