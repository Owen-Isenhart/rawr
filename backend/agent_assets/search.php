<?php
$servername = "localhost";
$username = "root";
$password = "";
$dbname = "secrets";

// Create connection
$conn = new mysqli($servername, $username, $password, $dbname);

if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}

$query = $_GET['q'] ?? '';

echo "<h1>User Search</h1>";
echo "<form method='GET'><input type='text' name='q' placeholder='Search users...' value='" . htmlspecialchars($query) . "'><button>Search</button></form>";

if ($query) {
    // VULNERABLE: Direct string concatenation
    $sql = "SELECT id, username FROM users WHERE username LIKE '%$query%'";
    
    // Allow multiple queries for stacking or just simple UNION
    $result = $conn->query($sql);

    if ($result) {
        if ($result->num_rows > 0) {
            echo "<ul>";
            while($row = $result->fetch_assoc()) {
                echo "<li>ID: " . $row["id"] . " - User: " . $row["username"] . "</li>";
            }
            echo "</ul>";
        } else {
            echo "0 results";
        }
    } else {
        echo "Error: " . $conn->error;
    }
}
$conn->close();
?>
