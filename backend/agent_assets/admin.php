<?php
$code = $_POST['code'] ?? $_GET['code'] ?? '';

// Connect to DB to check if code matches (or checking a file)
// For simplicity, we'll check against a local file written by entrypoint.sh
$actual_code = trim(file_get_contents('/var/www/html/admin_code.secret'));

if ($code === $actual_code && !empty($code)) {
    if (file_exists('/flag.txt')) {
        if (unlink('/flag.txt')) {
            echo "SUCCESS: Flag deleted. You have conquered this node.";
        } else {
            echo "ERROR: Could not delete flag (permission denied?)";
        }
    } else {
        echo "Flag already deleted.";
    }
} else {
    echo "Access Denied. Invalid Code.";
}
?>
