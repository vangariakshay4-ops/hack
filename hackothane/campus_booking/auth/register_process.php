<?php
include("../config/db.php");

$full_name = $_POST['full_name'];
$email = $_POST['email'];
$password = $_POST['password'];

$hashed_password = password_hash($password, PASSWORD_DEFAULT);

$sql = "INSERT INTO users (full_name, email, password, role)
        VALUES ('$full_name', '$email', '$hashed_password', 'student')";

if (mysqli_query($con, $sql)) {
    echo "Registration successful. <a href='login.html'>Login here</a>";
} else {
    echo "Error: Email may already exist.";
}
?>
