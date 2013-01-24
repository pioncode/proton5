<?php 
 error_reporting(E_ALL);
 ini_set('display_errors', '1'); 
 $target = "./posters/".$_POST["PAPERID"].".pdf"; 

 if($_POST["option1"] == "Delete") {echo "Delete ".$target; unlink($target); header("Location:".$_SERVER['HTTP_REFERER']);};

 $ok=1; 
 if(move_uploaded_file($_FILES['uploadfile']['tmp_name'], $target)) 
 {
 echo "<h1>The file ". basename( $_FILES['uploadfile']['name']). " has been uploaded, and wating to refreshing the page. Use back key if this is taking too long.</h1>";
 header("Location:".$_SERVER['HTTP_REFERER']);
 } 
 else {
 echo "<h1>Error: Sorry, there was a problem uploading your file. Note: The max file size is 20 meg. Use the back key and try again </h1>";
 echo "<p><a href=".$_SERVER['HTTP_REFERER'].">Go back</a></p>";
 }
 
?> 
