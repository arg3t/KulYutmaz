<?php
    if($_GET["xss"] == "vuln"){
        header('Location: /redirect.php?test=%253C');
    }else if($_GET["xss"] == "safe"){
        header('Location: /redirect.php?test=notvuln');
    }
?>
